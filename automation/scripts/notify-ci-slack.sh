#!/usr/bin/env bash
# JUnit XML 결과를 파싱해 Slack Webhook으로 CI 테스트 결과를 알린다.
# 사용법: notify-ci-slack.sh <junit-xml-path>
# 필요 환경변수: SLACK_WEBHOOK_URL
set -euo pipefail

JUNIT_XML_PATH="${1:?JUnit XML 경로를 첫 번째 인자로 전달해야 합니다.}"

if [ -z "${SLACK_WEBHOOK_URL:-}" ]; then
  echo "SLACK_WEBHOOK_URL이 설정되지 않아 Slack 알림을 건너뜁니다." >&2
  exit 0
fi

if [ ! -f "$JUNIT_XML_PATH" ]; then
  echo "JUnit XML 파일을 찾을 수 없어 Slack 알림을 건너뜁니다: $JUNIT_XML_PATH" >&2
  exit 0
fi

PAYLOAD=$(python3 - "$JUNIT_XML_PATH" <<'PYEOF'
import json
import re
import sys
import xml.etree.ElementTree as ET

path = sys.argv[1]
root = ET.parse(path).getroot()
suite = root.find("testsuite") if root.tag == "testsuites" else root

total = int(suite.get("tests", 0))
failures = int(suite.get("failures", 0))
errors = int(suite.get("errors", 0))
skipped = int(suite.get("skipped", 0))
passed = total - failures - errors - skipped
failed_count = failures + errors

# pytest는 실패 지점을 "<파일>:<줄번호>:" 형태로, 실제 에러 메시지는 "E "로 시작하는
# 줄로 표시한다(예: "tests/test_search.py:60: AssertionError" + "E   assert ..."). 이
# 두 가지를 뽑아내면 "어느 파일에서" + "로그상 이유"를 함께 보여줄 수 있다.
FILE_LINE_RE = re.compile(r"\b([\w./]+\.py:\d+):")


def _extract_file_ref(text):
    matches = FILE_LINE_RE.findall(text)
    # 라이브러리(selenium 등) 내부 프레임보다 테스트 코드 자신의 위치가 더 유용하므로
    # tests/ 아래 경로를 우선하고, 없으면 첫 매치를 사용한다.
    for m in matches:
        if m.startswith("tests/"):
            return m
    return matches[0] if matches else None


def _extract_reason(text, fallback):
    e_lines = [line[1:].strip() for line in text.splitlines() if line.startswith("E ") or line == "E"]
    if not e_lines:
        return fallback
    reason = " ".join(e_lines[:3])
    return reason[:300]


def _extract_tc_id(testcase):
    properties = testcase.find("properties")
    if properties is None:
        return "-"
    for prop in properties.findall("property"):
        if prop.get("name") == "tc_id":
            return prop.get("value") or "-"
    return "-"


# 상품 상태/가격/검색 순위 등 실제 판매 데이터가 바뀌어 테스트가 skip된 경우,
# conftest.py의 _skip_for_data_drift/_skip_if_product_status_changed가 이 접두어로 표시한다.
# 실패 목록에는 안 잡히지만 방치하면 커버리지가 조용히 줄어들므로 별도로 노출한다.
DATA_DRIFT_SKIP_PREFIX = "[TEST DATA DRIFT]"

drift_skips = []
for testcase in suite.findall("testcase"):
    node = testcase.find("skipped")
    if node is None:
        continue
    message = (node.get("message") or "").strip()
    if not message.startswith(DATA_DRIFT_SKIP_PREFIX):
        continue
    tc_id = _extract_tc_id(testcase)
    name = testcase.get("name", "")
    drift_skips.append(f"• `{tc_id}` {name} — {message}")

drift_block = ""
if drift_skips:
    drift_block = f"\n\n:warning: 데이터 변경 추정 SKIP {len(drift_skips)}건\n" + "\n".join(drift_skips)

if failed_count == 0:
    color = "#2eb67d"
    text = f":white_check_mark: 자동화 테스트 성공 — {passed}/{total} PASSED" + drift_block
else:
    lines = [f":x: 자동화 테스트 실패 — {failed_count}/{total} FAILED (통과 {passed}건)", ""]
    for testcase in suite.findall("testcase"):
        node = testcase.find("failure")
        if node is None:
            node = testcase.find("error")
        if node is None:
            continue
        classname = testcase.get("classname", "")
        name = testcase.get("name", "")
        body = node.text or ""
        fallback_message = (node.get("message") or "").splitlines()[0][:200]
        file_ref = _extract_file_ref(body) or f"{classname.replace('.', '/')}.py"
        reason = _extract_reason(body, fallback_message)
        tc_id = _extract_tc_id(testcase)
        lines.append(f"• `{tc_id}` `{file_ref}` — {name}\n  {reason}")
    color = "#e01e5a"
    text = "\n".join(lines) + drift_block

print(json.dumps({"attachments": [{"color": color, "text": text}]}))
PYEOF
)

curl -sf -X POST -H "Content-type: application/json" --data "$PAYLOAD" "$SLACK_WEBHOOK_URL" > /dev/null
echo "Slack 알림을 전송했습니다."
