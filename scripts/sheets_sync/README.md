# sheets_sync

TC Markdown 문서(`docs/tc/{feature-slug}.md`)를 Google Spreadsheet에 검토용으로 반영하고(승인 전 초안 포함),
자동화 후보 평가 결과(`docs/tc/automation-candidates/{feature-slug}.md`)를 Google Spreadsheet와
동기화하기 위한 CLI. `tc-agent`와 `automation-candidate-agent`가 Bash로 이 스크립트만
호출하며, Google Sheets를 직접 제어하지 않는다.

## 설치

```bash
pip install -r scripts/sheets_sync/requirements.txt
```

## 사전 준비 (최초 1회)

1. Google Cloud Console에서 프로젝트를 만들고 **Google Sheets API**를 활성화한다.
2. 서비스 계정(Service Account)을 생성하고 JSON 키 파일을 다운로드한다.
3. 반영 대상 Google Spreadsheet를 열어, 위 서비스 계정 이메일(`...@...iam.gserviceaccount.com`)을
   **편집자(Editor)** 권한으로 공유한다.
4. 프로젝트 루트에 `.env` 파일을 만들고 아래 값을 채운다 (`.env`는 `.gitignore`에 포함되어 있으므로
   커밋되지 않는다).

```bash
GOOGLE_SERVICE_ACCOUNT_FILE=/absolute/path/to/service-account.json
GOOGLE_SHEET_ID=스프레드시트_URL의_d와_edit_사이_값
# 선택: 기본 워크시트명은 "TC" — 다른 이름을 쓰려면 아래를 설정
# GOOGLE_SHEET_WORKSHEET=TC
# 선택: Feature Risk Matrix(별도 스프레드시트, Google Sheets 형식)를 읽을 때만 필요
# GOOGLE_RISK_SHEET_ID=리스크분석서_URL의_d와_edit_사이_값
```

`GOOGLE_SHEET_ID`는 스프레드시트 URL `https://docs.google.com/spreadsheets/d/{ID}/edit`에서
`{ID}` 부분이다.

## 사용법

### 기존 TC 조회

```bash
python scripts/sheets_sync/sheets_sync.py list
python scripts/sheets_sync/sheets_sync.py list --ids-only
python scripts/sheets_sync/sheets_sync.py list --worksheet Testcase_Cart
```

### Feature별 워크시트

- `append`/`pull`은 `--worksheet`를 생략하면 입력 파일명으로 Feature별 시트를 사용한다.
  `docs/tc/search.md` → `Testcase_Search`, `cart.md` → `Testcase_Cart`, `product-detail.md` → `Testcase_Product_Detail`.
  시트가 없으면 `append` 실제 실행 시 새로 만든다(dry-run은 만들지 않음).
- `--worksheet`를 지정하면 그 이름이 우선한다. `list --feature search`로 Feature 시트를 조회할 수 있다.
- Regression 시트 생성은 `--source-worksheet Testcase_Search Testcase_Cart ...`처럼 여러 Feature 시트를 함께 지정한다.

### TC 검토 흐름 (초안 → 시트 → 사용자 수정 → 역동기화 → 승인)

1. AI가 초안(`상태: 초안`)을 `append`로 시트에 반영한다(검토용 사본).
2. 사용자가 시트에서 직접 검토·수정한다. 검토 중에는 **시트가 기준**이다.
3. 사용자가 요청하면 `pull`로 시트 내용을 md에 반영한다.
4. 사용자가 채팅에서 명시 승인하면 md를 `승인완료`로 변경한다. `Regression 여부`는 승인 후 입력한다.

### 시트 → md 역동기화 (pull)

```bash
python scripts/sheets_sync/sheets_sync.py pull --input docs/tc/search.md --dry-run
python scripts/sheets_sync/sheets_sync.py pull --input docs/tc/search.md
python scripts/sheets_sync/sheets_sync.py pull --input docs/tc/cart.md --worksheet Testcase_Cart
```

- ID 기준으로 시트와 md를 비교해 `[수정됨]`(시트 값으로 md 행 갱신), `[시트에만 있음]`(md 첫 TC 표
  끝에 추가), `[md에만 있음]`(자동 삭제하지 않고 보고만)을 출력한다.
- **시트에는 쓰지 않는다.** md 파일만 수정하며 `--dry-run`이면 md도 수정하지 않는다.
- `Regression 여부` 열은 비교·반영하지 않는다. 같은 워크시트의 다른 Feature 행(ID 접두어가 다른 행)은 무시한다.
- Priority 산정 근거와 변경 이력은 `pull`이 갱신하지 않으므로 별도로 정리한다.

### TC 추가 (append-only)

```bash
# 1) 먼저 dry-run으로 반영될 내용을 미리 확인한다 (ID 충돌 여부 포함)
python scripts/sheets_sync/sheets_sync.py append --input docs/tc/cart.md --worksheet Testcase_Cart --dry-run

# 2) 문제 없으면 실제로 반영한다
python scripts/sheets_sync/sheets_sync.py append --input docs/tc/cart.md --worksheet Testcase_Cart
```

`--worksheet`를 생략하면 `GOOGLE_SHEET_WORKSHEET` 환경변수(없으면 기본값 `TC`) 하나의
워크시트에 모아서 반영한다. Feature별로 별도 시트에 반영하려면 매번 `--worksheet`로
대상 시트명을 지정한다(예: `Testcase_Search`, `Testcase_ProductDetail`, `Testcase_Order`,
`Testcase_Wishlist`, `Testcase_Cart`).

- 입력 파일 하나에 "## TC 목록", "## 결함 의심 항목" 등 여러 개의 TC 표가 있어도, 컬럼 구성이
  `tc-writing` Skill의 10개 컬럼 정의(`ID, 1 Depth, 2 Depth, 3 Depth, Preconditions, Test Steps, Expected Result, Priority, Requirement ID, Result`)와 일치하는 표는 모두 찾아 하나로 합쳐 반영한다.
- 이 스크립트는 **append(추가)만 수행**하며, 기존 행을 수정하거나 삭제하지 않는다.
- 입력 파일의 TC ID가 Spreadsheet에 이미 존재하는 ID와 충돌하면, 아무 것도 반영하지 않고
  전체를 중단한다(부분 반영 없음). 이 경우 기존 TC를 실제로 수정해야 하는지 사용자와 함께
  결정한 뒤, 필요하면 Spreadsheet를 수동으로 수정하거나 별도 방법을 논의한다.
- 대상 워크시트(기본값 `TC`)가 아직 없으면, `append` 실행 시(실제 반영 시에만, dry-run에서는
  생성하지 않음) 11개 컬럼 헤더(10개 TC 컬럼 + `Regression 여부`)와 함께 새로 만든다.
- md 표 셀의 `<br>`(`<br/>`, `<br />` 포함)는 `append` 시 시트의 **실제 줄바꿈**으로 변환된다. 새로 만든
  워크시트의 D~G열(3 Depth~Expected Result)에는 텍스트 줄바꿈 서식도 설정한다. `pull`은 시트의
  줄바꿈을 `<br>`로 되돌려 md에 반영하므로 변환은 왕복 대칭이다. 기존 워크시트의 행·서식은 수정하지 않는다.
- Spreadsheet의 마지막 열 `Regression 여부`는 **사용자가 직접 O/X를 입력하는 영역**이다. `append`는
  이 열을 항상 빈 값으로 추가하며 어떤 명령도 이 열에 값을 쓰지 않는다. Markdown TC 문서의 표는
  10개 컬럼 그대로이며 이 열은 Sheet에만 존재한다.
- 기존 워크시트의 헤더가 11개 컬럼 정의와 다르면(예: `Feature` 컬럼이 있는 이전 형식 시트, 이 경우 새 워크시트를 사용) 아무 것도 반영하지
  않고 중단한다. 이 경우 새 워크시트 이름을 `--worksheet`로 지정한다.

### Risk 스프레드시트 탭 조회 (읽기 전용)

```bash
python scripts/sheets_sync/sheets_sync.py sheet-tabs
python scripts/sheets_sync/sheets_sync.py sheet-read --worksheet "QA plan"
python scripts/sheets_sync/sheets_sync.py sheet-read --worksheet "리스크 테이블" --header-row 5
```

- `GOOGLE_RISK_SHEET_ID` 파일의 탭 목록(`sheet-tabs`)과 임의 탭 내용(`sheet-read`)을 조회만 한다.
- TC 생성 시 참고하는 탭: `QA plan`, `리스크 기반 테스트 전략`, `리스크 테이블`, `리스크 매트릭스`,
  `리스크 기반 테스트 전략 수립절차`, `리스크 팩터 정의`(Priority 산정 기준).
  헤더 행은 `QA plan`·`리스크 기반 테스트 전략 수립절차`·`리스크 팩터 정의`가 1행(문서형)이고
  `리스크 기반 테스트 전략`·`리스크 테이블`·`리스크 매트릭스`는 5행이다(`--header-row 5`).

### Feature Risk Matrix 조회 (읽기 전용)

```bash
python scripts/sheets_sync/sheets_sync.py risk-list
python scripts/sheets_sync/sheets_sync.py risk-list --worksheet "리스크 매트릭스" --header-row 5
```

- 리스크분석서는 TC용 스프레드시트와 **별도 파일**이므로 `GOOGLE_RISK_SHEET_ID`로 지정한다.
  파일은 Google Sheets 형식이어야 하며(.xlsx 형식은 Sheets API로 읽을 수 없음), 서비스 계정
  이메일에 **뷰어(Viewer)** 이상으로 공유해야 한다.
- 기본 탭은 `리스크 매트릭스`(`GOOGLE_RISK_WORKSHEET`로 변경 가능)이며, 상단 제목 행이 있어
  헤더는 5행이다(`--header-row`). 이 명령은 쓰기 호출을 하지 않는다.

### Regression TC 조회 (읽기 전용)

```bash
python scripts/sheets_sync/sheets_sync.py regression-list --source-worksheet TC
python scripts/sheets_sync/sheets_sync.py regression-list --source-worksheet TC --ids-only
```

- 전체 TC 워크시트에서 `Regression 여부`가 `O`인 TC를 10개 TC 컬럼으로 출력한다(`automation-candidate-agent`가
  평가 대상을 읽을 때 사용). 선택 규칙과 중단 조건은 아래 `regression-create`와 같고 쓰기 호출은 없다.

### Regression 워크시트 생성

```bash
# 1) dry-run으로 대상 TC를 미리 확인한다
python scripts/sheets_sync/sheets_sync.py regression-create --source-worksheet TC --worksheet "Regression TC" --dry-run

# 2) 사용자 승인 후 실제로 생성한다
python scripts/sheets_sync/sheets_sync.py regression-create --source-worksheet TC --worksheet "Regression TC"
```

- 사용자가 전체 TC 워크시트의 `Regression 여부` 열에 입력한 값이 `O`인 TC만 새 워크시트에 10개 TC
  컬럼으로 복사한다(`O`는 공백 제거·대소문자 무시). TC ID는 원본 그대로 유지된다.
- `--source-worksheet`는 여러 개를 지정할 수 있다(Feature별 워크시트를 쓰는 경우).
- 다음 경우에는 아무 것도 생성하지 않고 중단한다: 원본 헤더가 11개 컬럼 정의와 다름, `O`/`X`가
  아니거나 비어 있는 행이 있음(해당 행 목록 출력), `O`가 0건, `O` TC의 ID가 중복됨, 대상
  워크시트가 이미 존재함.
- 원본 워크시트에는 어떤 쓰기도 하지 않는다.

### 자동화 후보 평가 동기화

`automation-candidate-agent`가 사용하는 명령이다. Candidate 문서의 "AI 평가 결과" 표(TC ID +
6개 평가 축 + Automation Score + Candidate(AI) + 선정/제외 사유, 총 10개 컬럼)만 Spreadsheet에
반영하며, 사용자가 Sheet에 직접 입력하는 `QA Decision` / `QA Comment` 컬럼은 어떤 경우에도
쓰지 않는다.

```bash
# 1) 최초 1회: 자동화 후보 워크시트 생성 (이미 있으면 오류 — 정상 동작)
python scripts/sheets_sync/sheets_sync.py candidate-create-worksheet

# 2) Candidate 문서를 dry-run으로 미리 확인
python scripts/sheets_sync/sheets_sync.py candidate-sync --input docs/tc/automation-candidates/cart.md --dry-run

# 3) 문제 없으면 실제로 반영 (신규 TC는 새 행 추가, 기존 TC는 AI 영역만 갱신)
python scripts/sheets_sync/sheets_sync.py candidate-sync --input docs/tc/automation-candidates/cart.md

# 4) Sheet에 입력된 QA Decision/QA Comment를 포함해 전체 조회
python scripts/sheets_sync/sheets_sync.py candidate-list
```

- 기본 워크시트명은 `Automation Candidates`(모든 Feature가 하나의 워크시트를 공유하며, TC ID로
  구분한다). 다른 이름을 쓰려면 `--worksheet` 또는 `GOOGLE_SHEET_CANDIDATE_WORKSHEET` 환경변수를
  사용한다.
- `candidate-sync`는 입력 파일 안의 TC ID가 이미 Sheet에 존재하면 AI 작성 영역(A~J열)만
  덮어쓰고, `QA Decision`/`QA Comment`(K~L열)는 건드리지 않는다. 신규 TC ID는 새 행으로
  추가되며 이때 `QA Decision`/`QA Comment`는 빈 값으로 시작한다.
- 워크시트 헤더가 Candidate 컬럼 정의와 다르면(예: 사용자가 임의로 컬럼을 바꾼 경우) 안전을
  위해 아무 것도 반영하지 않고 중단한다.

## 환경변수 요약

| 변수 | 필수 | 설명 |
|---|---|---|
| `GOOGLE_SERVICE_ACCOUNT_FILE` | 예 | 서비스 계정 JSON 키 파일의 로컬 경로 |
| `GOOGLE_SHEET_ID` | 예 | 대상 Google Spreadsheet ID |
| `GOOGLE_SHEET_WORKSHEET` | 아니오 (기본값 `TC`) | `list`/`append`의 대상 워크시트(탭) 이름 |
| `GOOGLE_SHEET_CANDIDATE_WORKSHEET` | 아니오 (기본값 `Automation Candidates`) | `candidate-*` 명령의 대상 워크시트(탭) 이름 |
| `GOOGLE_SHEET_REGRESSION_WORKSHEET` | 아니오 (기본값 `Regression TC`) | `regression-create`가 생성할 워크시트(탭) 이름 |
| `GOOGLE_RISK_SHEET_ID` | `risk-list` 사용 시 | Feature Risk Matrix가 있는 별도 Google Spreadsheet ID |
| `GOOGLE_RISK_WORKSHEET` | 아니오 (기본값 `리스크 매트릭스`) | `risk-list`의 대상 워크시트(탭) 이름 |

## 제한 사항

- `list`/`append`/`pull`(md만 수정)/`risk-list`/`sheet-tabs`/`sheet-read`/`regression-list`/`regression-create`는 기존 행 수정(update)/삭제(delete) 기능을
  의도적으로 제공하지 않는다(`regression-create`는 새 워크시트를 만들 뿐 원본을 수정하지 않는다). 승인완료된 TC를 재수정해야 하는 경우는 `tc-agent`의 "승인완료 문서 재수정 시 처리"
  절차를 따르며, Spreadsheet 반영 방법은 그때 사용자와 함께 결정한다.
- `candidate-sync`만 예외적으로 기존 행의 AI 작성 영역(A~J열)을 갱신할 수 있다. 이는 재평가된
  TC의 점수를 반영하기 위한 것이며, 컬럼 범위가 AI 작성 영역으로 고정되어 있어 사용자 작성 영역
  (`QA Decision`/`QA Comment`)은 어떤 경우에도 덮어쓰지 않는다. 삭제 기능은 여전히 제공하지
  않는다.
- 이 스크립트는 인증/네트워크 오류를 그대로 사용자에게 보고하며, 임의로 재시도하거나 오류를
  숨기지 않는다.
