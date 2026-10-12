# Development Guidelines - laftel-store QA Automation

이 문서는 이 저장소에서 작업하는 AI Agent(Claude Code 및 모든 Sub Agent/Skill)를 위한
**프로젝트 고유 운영 규칙**이다. 일반적인 개발 지식이나 CLAUDE.md에 이미 정의된 승인/추적성
원칙의 재설명은 포함하지 않는다. `CLAUDE.md`와 내용이 충돌하면 `CLAUDE.md`가 우선한다.

## 1. Project Overview

- Claude Code + MCP(Shrimp Task Manager, Playwright)를 이용해 `store.laftel.net`(라프텔
  스토어)의 QA 프로세스(PRD → 전체 TC → 사용자의 Regression 범위 지정 → 자동화 대상 선정 →
  Roadmap → 자동화 코드 → CI 정기 실행 → Slack 알림)를 사람 승인 지점을 유지한 채 자동화하는
  프로젝트다. 핵심 목표는 CLAUDE.md 1~2절을 따른다.
- **산출물과 코드의 현재 상태는 이 문서에 적지 않는다.** 항상 실제 파일(Repository Code)과 각
  문서의 frontmatter `상태` 필드로 직접 확인한다(CLAUDE.md 8절).
- 기술 스택 결정: Python + Selenium + pytest + POM (`docs/automation/AUTOMATION_GUIDE.md`
  1~4절이 Source of Truth). Roadmap/TC/PRD 세부 판단 우선순위는 `CLAUDE.md` 8절 표를
  그대로 따른다.

## 2. Directory & File Map (실제 존재 여부 기준)

| 경로 | 용도 |
|---|---|
| `CLAUDE.md` | 최상위 원칙 (모든 Agent/Skill보다 우선) |
| `shrimp-rules.md` | AI Agent 운영 규칙(이 문서) |
| `docs/prd/project-prd.md` | Project PRD |
| `docs/prd/Feature/prd-{slug}.md` | Feature PRD |
| `docs/tc/{slug}.md` | 원본 TC(전체 기능 TC, 승인 후 Google Sheet에 반영) |
| `docs/tc/automation-candidates/{slug}.md` | 자동화 후보 평가 + Approved TC 목록 |
| `docs/roadmap/ROADMAP.md` | Phase별 구현 Roadmap |
| `docs/automation/AUTOMATION_GUIDE.md` | Python 자동화 코드 작성 규칙 (Source of Truth) |
| `scripts/sheets_sync/sheets_sync.py` | Google Sheets 연동 CLI (TC 반영, Risk Matrix 읽기, Regression 조회/생성, Candidate 평가) |
| `.claude/agents/*.md`, `.claude/agents/dev/*.md` | Sub Agent 정의 |
| `.claude/skills/*/SKILL.md` | 평가/작성 규칙 Skill (`tc-writing`, `automation-candidate`) |
| `automation/` | 자동화 코드와 공통 기반(conftest.py, config, pytest.ini, requirements.txt, scripts 등). 구조는 AUTOMATION_GUIDE 3절 |
| `.github/workflows/` | CI 워크플로우 (AUTOMATION_GUIDE 16절, CLAUDE.md 15절) |
| `.env` (`.gitignore`에 포함) | Google 서비스 계정 경로, Sheet ID(TC용/Risk Matrix용), 테스트 계정 정보 |

- `docs/`, `.claude/agents/`, `.claude/skills/`, `scripts/sheets_sync/` 하위 기존 파일을
  새 파일 생성 전에 항상 먼저 확인한다 — 동일 역할의 파일을 중복 생성하지 않는다.
- `automation/` 하위 코드의 import 경로는 AUTOMATION_GUIDE 3.1절 규칙(`automation.` prefix 없이
  `automation/`을 루트로 import)을 따르고, 새 구현의 첫 테스트 실행 시점에 동작을 확인한다.

## 3. Document State Machine (문서별 상태 필드)

모든 산출물 Markdown은 frontmatter에 `상태` 필드를 가지며, 아래 전이만 허용된다. **하위
단계 Agent는 상태가 요구 조건에 미달한 상위 문서를 입력으로 사용하지 않는다.**

| 문서 | 상태 값 및 순서 | 다음 단계 입력 조건 |
|---|---|---|
| `docs/prd/project-prd.md`, `docs/prd/Feature/prd-{slug}.md` | `초안` → `승인완료` | `상태: 승인완료`만 TC 생성 근거로 사용 가능 |
| `docs/tc/{slug}.md` | `초안` → `승인완료` | `상태: 승인완료`만 자동화 후보 평가 근거로 사용 가능 |
| `docs/tc/automation-candidates/{slug}.md` | `평가중` → `사용자검토완료` → `자동화대상확정` | Roadmap/자동화 코드는 문서 전체가 `자동화대상확정`이고 그 안에서 `QA Decision: Approved`인 TC만 사용 가능 (`Hold`/`Rejected`/미검토 제외) |
| `docs/roadmap/ROADMAP.md` | `초안` → `승인완료` | 자동화 코드 구현은 `상태: 승인완료`만 입력으로 사용 |
| `docs/automation/AUTOMATION_GUIDE.md` | `초안` → `승인완료` | Roadmap/구현 모두 `상태: 승인완료`가 아니면 진행 금지 |

- **Regression 범위는 문서 상태가 아니라 Google Sheet의 "전체 TC 워크시트 → Regression 여부 = O"
  값(사용자 입력)이 Source of Truth다.** 자동화 후보 평가 대상 TC는 이 값과 `상태: 승인완료`인
  원본 TC 문서에 모두 해당해야 한다.
- 단계를 건너뛰어 임의로 최종 상태로 전환하지 않는다(예: Candidate 문서를 `평가중`에서
  바로 `자동화대상확정`으로 바꾸지 않음).
- 이미 최종 상태인 문서를 재수정해야 할 때는 각 Agent 정의 파일의 "승인완료(또는
  자동화대상확정) 문서 재수정 시 처리" 절차를 그대로 따른다(임의 직접 수정 금지).

## 4. Coding Convention (문서 vs 코드 구분)

- **Markdown 산출물(`docs/`, `.claude/agents/`, `.claude/skills/`)**: 전역
  `~/.claude/CLAUDE.md` 규칙 적용 — 한국어 서술, 변경 이력에 날짜/사유 기록.
- **Python 자동화 코드(`automation/` 하위)**: 전역 CLAUDE.md의
  "2칸 들여쓰기/camelCase" 규칙이 아니라 `AUTOMATION_GUIDE.md` 1.1절 예외를 적용한다.
  - 들여쓰기 4칸, 변수/함수명 snake_case, 클래스명 PascalCase, 상수 UPPER_SNAKE_CASE.
  - 주석은 한국어(전역 CLAUDE.md 유지), 변수/함수명은 영어.
  - 이 예외는 `automation/` 하위 Python 코드에만 적용되며, `scripts/sheets_sync`(기존
    Python 도구 스크립트)의 기존 컨벤션을 바꾸지 않는다. `scripts/sheets_sync` 신규
    코드도 기존 스크립트 스타일을 따른다(임의로 4칸/2칸을 뒤섞지 않음).
- Page Object 클래스는 `~Page` 접미사 필수, 모든 Page 클래스는 `BasePage` 상속,
  Locator는 클래스 상단 `UPPER_SNAKE_CASE` 상수, Full XPath와 `time.sleep()` 금지 —
  상세는 AUTOMATION_GUIDE 4~7·18절.

## 5. Agent/Skill 책임 경계 (임의로 침범 금지)

| Agent | 유일한 책임 | 반드시 로드하는 Skill | 하지 않는 것 |
|---|---|---|---|
| `prd-agent` | Project/Feature PRD 작성 | 없음 | TC/Roadmap/코드 생성, Git 작업 |
| `tc-agent` | 전체 기능 TC 작성 + Google Sheet 반영, 사용자 승인 후 Regression 시트 생성(선택 기능), Risk Matrix 읽기(참고) | `tc-writing` | PRD 판단 기준 자체 정의, Sheet 직접 API 호출(스크립트 경유만), "Regression 여부" 열 입력 및 Regression 범위 결정 |
| `automation-candidate-agent` | 사용자 요청 시 Regression(O) TC의 자동화 후보 평가 + QA Decision 검증/확정 | `automation-candidate` | TC/PRD 수정, 자동화 코드/Roadmap 생성, QA Decision 임의 변경, "Regression 여부" 열 입력 |
| `roadmap-agent` | Phase별 Roadmap 작성(Repository 현황 확인 포함) | 없음(AUTOMATION_GUIDE를 Source of Truth로 참조) | Shrimp Task 생성, 코드 작성, PRD/TC/Candidate 문서 수정 |
| `ci-agent` | CI 워크플로우 구성, 트리거별 실행 범위 반영, Slack 알림 스크립트, 정기 실행 활성화 관리 | 없음(CLAUDE.md 15절, AUTOMATION_GUIDE 16절 참조) | 테스트 코드/pytest marker 부여, Commit/Push, Secret 값 읽기·설정, 정기 실행 대상·주기·환경 무승인 변경, 실행 시점 승인 게이트 구현, CI 실패 분석/Quality Reporting |
| `automation-developer-agent` | 자동화 코드 구현 + pytest 실행 | 없음(AUTOMATION_GUIDE 참조) | 코드 리뷰, Git Commit/Push, 상위 산출물 임의 수정, CI/Slack 연동 |
| `quality-agent` | 사용자 요청 시 GitHub Actions 결과 기반 실패 원인 분류·분석, Quality Report 작성 | 없음(CLAUDE.md 13절, AUTOMATION_GUIDE 14·16절 참조) | 테스트 코드/CI 구성 수정, Commit/Push, CI 재실행(`gh run rerun`/`gh workflow run`), Secret 읽기·설정, Slack 발송, 실패를 PASS로 판단, 실패 TC당 2회 이상 재실행 |

- CI 워크플로우 변경(Roadmap의 Phase Final)은 `ci-agent`가 담당하며, `automation-developer-agent`는
  CI 워크플로우 작성과 Slack 알림 연동을 하지 않는다. CI 실패 분석과 Quality Reporting은
  `quality-agent`가 사용자 요청 시에만 수행한다(CI 시점의 결과 수집·리포트 생성·Slack 알림은
  CI와 `ci-agent`의 몫).
- 새 Agent/Skill이 필요하면 기존 Agent를 확장하지 말고 책임이 분리된 새 파일을 만든다
  (`CLAUDE.md` 6절).
- 각 Agent 정의 파일(`.claude/agents/**/*.md`)의 "공통 원칙/가드레일"·"Workflow" 절이
  해당 Agent의 상세 실행 규칙이다. 이 문서(`shrimp-rules.md`)와 개별 Agent 정의가 절차
  세부사항에서 다르게 보이면, 그 Agent의 작업에 한해서는 해당 Agent 정의 파일을 따른다.

## 6. 외부 도구 사용 규칙

### 6.1 `scripts/sheets_sync/sheets_sync.py` (Google Sheets 연동)

- **Google Sheets 접근은 반드시 이 CLI를 Bash로 호출하는 방식만 사용한다.** 별도 API
  호출 코드를 즉석에서 작성하지 않는다.
- 주요 명령: `list`, `append --input <path> [--worksheet <name>] [--dry-run]`,
  `risk-list`(Risk Matrix 읽기 전용), `regression-list`(Regression O TC 읽기 전용),
  `regression-create [--dry-run]`(O TC만 새 워크시트에 복사),
  `candidate-create-worksheet`, `candidate-sync --input <path> [--dry-run]`, `candidate-list`.
- `append`/`candidate-sync`/`regression-create`는 실제 반영 전 항상 `--dry-run`으로 먼저 확인한다.
- `append`는 append-only이며 기존 행을 수정/삭제하지 않는다. ID 충돌 시 전체 반영을
  중단한다 — `--force` 같은 우회 옵션은 없으며 만들지 않는다. 신규 워크시트는 `Regression 여부`
  열을 포함한 10컬럼 헤더로 생성되고 이 열은 항상 빈 값으로 추가된다. 이전 형식(9컬럼) 워크시트는
  헤더 불일치로 중단되며, 그 경우 새 워크시트 이름을 사용한다.
- `candidate-*` 명령은 사용자가 확인한 Candidate 워크시트 이름을 `--worksheet`로 명시해 사용한다
  (이전 평가 데이터가 섞이는 것을 막기 위함).
- `candidate-sync`는 AI 작성 영역(TC ID + 6개 평가 축 + Automation Score +
  Candidate(AI) + 선정/제외 사유, 10개 컬럼)만 갱신한다. `QA Decision`/`QA Comment`
  컬럼은 어떤 방법으로도 쓰지 않는다(읽기는 `candidate-list`로만).
- 환경변수는 `.env`(`GOOGLE_SERVICE_ACCOUNT_FILE`, `GOOGLE_SHEET_ID`,
  `GOOGLE_SHEET_WORKSHEET`, `GOOGLE_SHEET_CANDIDATE_WORKSHEET`,
  `GOOGLE_SHEET_REGRESSION_WORKSHEET`, `GOOGLE_RISK_SHEET_ID`, `GOOGLE_RISK_WORKSHEET`)로만
  관리하며 코드/문서/대화에 Spreadsheet ID 등을 하드코딩하거나 노출하지 않는다.

### 6.2 Playwright MCP (`mcp__playwright__browser_*`)

- 용도는 **Selenium 코드 작성 전 실제 페이지 구조/Locator 조사**로 한정한다
  (`automation-developer-agent` 전용, AUTOMATION_GUIDE 5절).
- 프로덕션 테스트 실행 도구는 Selenium이며, Playwright MCP로 Selenium 실행을 대체하지
  않는다.
- 조회·탐색 목적에만 사용하고, 페이지 상태나 서비스 데이터를 변경하는 `browser_evaluate`
  실행(계정 생성/삭제, 주문 시도 등)은 금지한다.

### 6.3 Shrimp Task Manager MCP

- Shrimp Task(작업 분해)는 승인된 `docs/roadmap/ROADMAP.md`(상태: 승인완료)를 입력으로만
  생성한다. Roadmap이 초안이거나 없으면 Task를 생성하지 않는다.
- `DATA_DIR`는 `.mcp.json`에 `shrimp_data/`로 고정되어 있다 — 임의로 다른 경로를
  지정하지 않는다.

## 7. Key File Interaction (동시 갱신 필요 지점)

- **TC 표 컬럼(md 표 9개: ID/Requirement ID/Feature/Test Scenario/Preconditions/Test
  Steps/Expected Result/Priority/Result, Sheet는 뒤에 `Regression 여부`가 붙은 10개)의 순서나
  개수를 바꾸려면** 반드시 `.claude/skills/tc-writing/SKILL.md` 2절과
  `scripts/sheets_sync/sheets_sync.py`의 `TC_COLUMNS`(md 파싱용)/`SHEET_TC_COLUMNS`(Sheet용)를
  **함께** 수정한다. 한쪽만 바꾸면 `append`/`regression-*`/`candidate-sync` 동작이 깨진다.
- **"Regression 여부" 열 이름을 바꾸려면** `sheets_sync.py`의 `REGRESSION_COLUMN`, `tc-agent.md`,
  `automation-candidate-agent.md`, `CLAUDE.md`(3·8·18절)를 **함께** 수정한다.
- **Candidate AI 평가 표 컬럼(10개: TC ID + 6개 축 + Automation Score +
  Candidate(AI) + 선정/제외 사유)을 바꾸려면** `.claude/skills/automation-candidate/
  SKILL.md` 8절과 `sheets_sync.py`의 `CANDIDATE_AI_COLUMNS`를 **함께** 수정한다.
- **`docs/tc/{slug}.md`(원본 TC)가 재승인으로 변경되면**, 해당 Feature의
  `docs/tc/automation-candidates/{slug}.md`가 무효화될 수 있다 — Candidate 문서
  프런트매터의 "대상 TC 문서 최근 변경일"과 비교해 재평가 필요 여부를 확인한다
  (`automation-candidate-agent` 워크플로우 3번).
- **Candidate 문서의 Approved TC 목록이 바뀌면**, `docs/roadmap/ROADMAP.md`의 대상
  TC 수·Phase 매핑표가 최신 상태와 어긋날 수 있다 — Roadmap을 그대로 재사용하지 말고
  Candidate 문서를 직접 재확인한다(`roadmap-agent` 가드레일).
- **확정 Approved TC 목록(정기 실행 대상)이 바뀌면**, CI 실행 범위(`.github/workflows/test.yml`과
  pytest 선택 설정)가 어긋날 수 있다. 정기 실행 대상 추가/제외와 주기·환경 변경은 CLAUDE.md
  18절에 따라 사용자 승인이 필요하다.
- **`docs/automation/AUTOMATION_GUIDE.md`가 변경되면**, 이미 작성된 `automation/` 코드
  중 변경된 절(Locator 우선순위, 디렉터리 구조 등)에 해당하는 부분의 재검토가 필요하다.
- **`.mcp.json`을 수정할 때**(서버 추가/경로 변경 등)는 `DATA_DIR`가 여전히 이 저장소의
  `shrimp_data/`를 가리키는지 확인한다 — 다른 프로젝트의 Shrimp 데이터와 섞이지 않도록
  한다.

## 8. AI Decision-making Standards

- **상위 산출물 상태가 요구 조건에 못 미치면(초안 상태 등) 즉시 중단하고 사용자에게
  안내한다.** 부족한 정보를 추정해서 다음 단계를 진행하지 않는다.
- **문서 간 내용이 충돌하면**(예: Candidate 문서의 TC ID가 원본 TC에 없음, Roadmap
  대상 TC 수가 Candidate 문서와 다름) 임의로 하나를 선택하지 않고 충돌 내용을 그대로
  사용자에게 보고한 뒤 확인을 받는다(`CLAUDE.md` 8절).
- **QA Decision 값 판단**: 정확히 `Approved`/`Rejected`/`Hold`(대소문자·공백까지 일치)만
  유효하다. 빈 값은 "미검토"로, 그 외 모든 값(`approved`, `승인`, 오탈자 등)은 Validation
  Error로 처리하며 임의 보정하지 않는다.
- **"Regression 여부" 값 판단**: `O`/`X`만 유효하다(공백·대소문자는 무시하며, `sheets_sync.py`
  구현 기준). 빈 값이나 그 외 값이 하나라도 있으면 Regression 범위 조회·시트 생성·평가를 중단하고
  해당 행을 사용자에게 보고하며, AI가 값을 채우거나 해석하지 않는다. (QA Decision은 이와 달리
  대소문자·공백까지 엄격하게 검증한다.)
- **자동화 대상 판단 조건은 항상 다음 두 조건의 AND다** — 어느 한쪽만으로 판단하지
  않는다.
  ```
  Candidate 문서 상태 = 자동화대상확정  AND  QA Decision = Approved
  ```
- **Git Commit/Push, Production 데이터 변경(계정 생성/삭제 등), Google Sheet 실제 반영
  (dry-run 아님)** 앞에서는 항상 실행 직전 결과를 사용자에게 보여주고 명시적 승인을
  받는다. "괜찮아 보인다" 같은 모호한 응답은 승인으로 간주하지 않는다.
- 코드/문서 작성을 완료로 보고하기 전에 관련 테스트(자동화 코드는 pytest, TC/Candidate
  문서는 각 스크립트의 `--dry-run`)를 실제로 실행해 결과를 확인한다. 실행하지 않고
  "완료"로 보고하지 않는다.

## 9. Prohibited Actions

- 승인된 상위 산출물(PRD/TC/Candidate/Roadmap/AUTOMATION_GUIDE)을 재승인 절차 없이
  직접 수정하는 것.
- `sheets_sync.py`의 사용자 작성 영역(`QA Decision`/`QA Comment`)을 어떤 명령으로도
  쓰는 것.
- `sheets_sync.py`가 제공하지 않는 행 수정/삭제 기능을 즉석 스크립트로 대체 구현하는 것.
- Google Sheet의 `Regression 여부` 열에 값을 쓰는 것(사용자 입력 영역).
- 이전 형식의 TC나 이전 자동화 후보 평가가 남은 워크시트에 같은 TC ID로 `append`/`candidate-sync`
  하는 것.
- 정기 실행 대상·주기·실행 환경을 사용자 승인 없이 변경하는 것(CLAUDE.md 18절).
- Playwright MCP로 Production 데이터를 변경(계정 생성/삭제, 주문 시도 등)하는 것.
- `automation/` 코드에서 Full XPath 사용, `time.sleep()` 사용, Page Layer에서
  Assertion 수행, 비밀번호 등 민감정보를 코드/로그/리포트/스크린샷에 노출하는 것.
- 사용자 승인 없이 Git Commit/Push를 수행하는 것.
- 현재 요청받은 단계의 다음 단계 산출물을 임의로 선행 생성하는 것(예: TC 작성 중
  Roadmap이나 자동화 코드를 미리 만드는 것).
- 다른 프로젝트에서 재사용 가능하도록 설계된 Skill(`tc-writing`,
  `automation-candidate`)에 이 프로젝트 전용 정보(URL, 계정 등)를 하드코딩하는 것.

## 변경 이력

| 날짜 | 변경 사유 |
|---|---|
| 2026-10-13 | 프로젝트 목표 재정의(리스크 기반 핵심 Regression 정기 실행)에 따른 갱신 — 낡은 상태 스냅샷(1·2절) 제거, Regression 범위(Sheet "Regression 여부")/Risk Matrix 읽기/`sheets_sync` 신규 명령 반영(3·5·6·7절), 값 판단 규칙(8절)과 금지 항목(9절) 추가, CI 변경 담당(`ci-agent`)과 실패 분석/Quality Reporting 담당(`quality-agent`) 추가 |
| 2026-09-05 | 최초 생성 — 기존 CLAUDE.md/Agent 정의/Skill/AUTOMATION_GUIDE/ROADMAP/sheets_sync 문서를 근거로 AI Agent 운영 규칙 초안 작성 |
