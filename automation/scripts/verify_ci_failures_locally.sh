#!/usr/bin/env bash
# CI(GitHub Actions)에서 실패한 테스트만 골라 로컬에서 재실행한다.
# AUTOMATION_GUIDE 7.22절(전체 스위트 15분+ 연속 실행 시 발생하는 일반적인 간헐적
# 타이밍 플레이키)로 의심되는 실패가 실제로 일시적 현상인지, 아니면 재현되는
# 진짜 문제인지 빠르게 구분하기 위한 용도다(CLAUDE.md 13절: 실패를 임의로 PASS로
# 판단하지 않고, 원인이 불명확하면 추측 대신 실측으로 확인한다).
#
# 사용법: scripts/verify_ci_failures_locally.sh [RUN_ID]
#   RUN_ID를 생략하면 main 브랜치의 가장 최근 CI 실행을 사용한다.
# 사전 조건: gh CLI 로그인 상태, 저장소 루트(또는 그 하위)에서 실행.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTOMATION_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

RUN_ID="${1:-}"
if [ -z "$RUN_ID" ]; then
  RUN_ID=$(gh run list --workflow="test.yml" --branch=main --limit=1 --json databaseId --jq '.[0].databaseId')
  if [ -z "$RUN_ID" ]; then
    echo "main 브랜치의 CI 실행 기록을 찾을 수 없습니다." >&2
    exit 1
  fi
  echo "RUN_ID 미지정 — 가장 최근 실행($RUN_ID)을 사용합니다."
fi

WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

echo "run ${RUN_ID}의 test-reports 아티팩트를 내려받는 중..."
if ! gh run download "$RUN_ID" -n test-reports -D "$WORK_DIR" >/dev/null 2>&1; then
  echo "아티팩트를 내려받지 못했습니다(실행이 아직 진행 중이거나, 아티팩트가 만료됐거나, RUN_ID가 올바르지 않을 수 있습니다)." >&2
  exit 1
fi

JUNIT_XML="$WORK_DIR/reports/results.xml"
if [ ! -f "$JUNIT_XML" ]; then
  echo "results.xml을 찾을 수 없습니다: $JUNIT_XML" >&2
  exit 1
fi

NODE_IDS=$(python3 - "$JUNIT_XML" <<'PYEOF'
import sys
import xml.etree.ElementTree as ET

path = sys.argv[1]
root = ET.parse(path).getroot()
suite = root.find("testsuite") if root.tag == "testsuites" else root

for testcase in suite.findall("testcase"):
    if testcase.find("failure") is None and testcase.find("error") is None:
        continue
    # junitxml의 classname은 "tests.test_search" 형태이므로 파일 경로로 되돌린다.
    module_path = testcase.get("classname", "").replace(".", "/") + ".py"
    name = testcase.get("name", "")
    print(f"{module_path}::{name}")
PYEOF
)

if [ -z "$NODE_IDS" ]; then
  echo "run ${RUN_ID}에는 실패한 테스트가 없습니다. 재검증할 대상이 없습니다."
  exit 0
fi

echo ""
echo "CI에서 실패한 테스트 목록:"
echo "$NODE_IDS" | sed 's/^/  - /'
echo ""
echo "로컬에서 재실행합니다(통과하면 7.22절의 알려진 타이밍 플레이키로 간주,"
echo "다시 실패하면 실제 문제일 수 있으므로 추가 조사가 필요합니다)..."
echo ""

cd "$AUTOMATION_DIR"
# shellcheck disable=SC2086
python3 -m pytest $NODE_IDS -v
