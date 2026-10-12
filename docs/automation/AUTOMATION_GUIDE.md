---
문서유형: Automation Guide
상태: 승인완료
참고: 이전 프로젝트(대상 사이트 automationexercise.com)에서 사용한 문서를 참고해, 라프텔
      스토어(store.laftel.net) 프로젝트에 맞게 재작성함. 2026-10-13 프로젝트 목표 재정의에 따라
      구 자동화 코드·구 TC 종속 서술을 정리함(규칙 부분은 유지)
최초 작성일: 2026-09-05
최근 변경일: 2026-10-13
승인일: 2026-09-05
---

# AUTOMATION_GUIDE.md - 라프텔 스토어 자동화 코드 개발 기준

## 0. 문서 목적 및 범위

이 문서는 이 프로젝트(라프텔 스토어 QA 자동화)의 **자동화 코드 개발 기준**을 정의하는
Source of Truth이며,
다음 작업에서 공통 판단 근거로 사용합니다.

- 자동화 개발 Roadmap 작성
- Shrimp Task 생성 및 작업 분해
- 자동화 코드 개발
- 코드 리뷰 및 테스트 실행/검증

이 문서는 **기능별 요구사항(로그인, 장바구니 등)을 다루지 않습니다.** 기능별 요구사항은
`docs/prd/Feature/prd-{slug}.md`(Feature PRD)와 승인된 TC를 Source of Truth로 합니다. 이 문서와
PRD/TC/Roadmap의 내용이 서로 다르게 보이면, 요구사항·시나리오 판단은 항상 PRD/TC를 기준으로
하고, **코드 작성 방식(구조/컨벤션/원칙)에 대한 판단만 이 문서를 기준으로** 합니다.

**현재 상태 (2026-10-13)**: 프로젝트 목표 재정의에 따라 기존 Feature별 테스트·Page Object·Locator
코드를 모두 삭제했습니다. 리스크 기반 Regression TC 설계 → 자동화 대상 선정 → 자동화 코드 생성
순서로 새로 구축하며, 현재 저장소에는 공통 기반(`conftest.py`, `config/`, `pytest.ini`,
`requirements.txt`, `scripts/`)과 CI 워크플로우(`.github/workflows/test.yml`)만 남아 있습니다.
실제 구현 상태가 이 문서와 달라지면(CLAUDE.md 8절 "실제 구현 상태 = Repository Code" 원칙에
따라) 문서를 갱신합니다.

### 0.1 자동화 대상 범위

이 문서가 정의하는 규칙이 적용되는 자동화 대상은, 사용자가 검토·확정한 Regression TC 중
**자동화 대상으로 최종 선정된 TC**입니다(`automation-candidate-agent`가 정의한 조건을
따릅니다). 구체적인 대상 목록과 건수는 새 TC 설계와 자동화 적합성 평가가 완료된 뒤 해당
산출물을 Source of Truth로 참조하며, 이 문서에 TC 목록을 복제하지 않습니다.

이 문서의 원칙 자체는 특정 Feature 목록에 종속되지 않고 재사용 가능하게 작성합니다.

---

## 1. Technology Stack

| 항목 | 결정 | 비고 |
|---|---|---|
| 언어 | **Python** | 1.1절 "코딩 스타일 예외" 적용 대상 |
| 자동화 도구 | **Selenium WebDriver** | |
| 테스트 러너 | **pytest** | |
| 설계 패턴 | **Page Object Model (POM)** | |
| 리포팅 | **pytest-html + JUnit XML(`--junitxml`) 병행** | HTML은 사람이 보는 Artifact, JUnit XML은 Slack 실패 메시지 조립용. `pytest.ini`의 `addopts`로 기본 경로(`reports/report.html`, `reports/results.xml`)가 고정되어 있어 로컬/CI 어디서 실행하든 옵션 없이 자동 생성되며, 별도 파일명이 필요하면 CLI에서 `--html`/`--junitxml`을 다시 지정해 덮어쓸 수 있다 |
| 실행 브라우저 | **Chrome (ChromeDriver)** | 일반 데스크톱 창 크기로 실행, 별도 모바일 에뮬레이션 미사용(사용자 결정 — 라프텔 스토어는 모바일 웹 기준 반응형 사이트이나 PC Chrome에서도 동일하게 동작함. 모바일 웹 자체 검증은 이번 범위 밖, 추후 별도 진행) |
| 대상 환경 | Production 단일 환경 (`https://store.laftel.net/`) | 별도 dev/staging 없음(Project PRD 3절), 장비 부족으로 PC Chrome에서만 검증(Project PRD 4절) |
| CI/CD | **GitHub Actions** | 트리거별 실행 범위는 새 TC 확정 후 결정(16절) |
| 알림 | **Slack** | 실패 시 실패 원인 요약 포함 알림(CLAUDE.md 16절: 승인 용도 아님, 결과 알림 전용) |
| 패키지 버전 관리 | `requirements.txt` | `automation/requirements.txt`에 고정 |

### 1.1 코딩 스타일 예외 (중요)

프로젝트 전역 CLAUDE.md는 "들여쓰기 2칸, camelCase/PascalCase(컴포넌트)"를 기본 스타일로
정의하지만, **Python 자동화 코드에 한해 다음과 같이 PEP8을 우선 적용하는 예외를 사용자
승인으로 확정합니다.**

- 들여쓰기: **4칸** (2칸 아님)
- 변수/함수명: **snake_case** (camelCase 아님)
- 클래스명: PascalCase (전역 규칙과 동일, 충돌 없음)
- 상수(Locator 등): UPPER_SNAKE_CASE

이유: `black`/`flake8` 등 Python 표준 도구 체인이 4칸 들여쓰기와 PEP8 네이밍을 전제로 하고,
Selenium/표준 라이브러리 API 자체가 snake_case이므로 일관성을 위해 예외를 인정합니다. 이
예외는 **이 프로젝트의 Python 자동화 코드에만 적용**되며, PRD/TC/Roadmap 등 Markdown
문서나 다른 언어로 작성될 도구(`scripts/sheets_sync`의 기존 코드 포함)의 컨벤션까지 바꾸는
것은 아닙니다.

---

## 2. Automation Architecture

- **Page Object Model (POM)**을 채택합니다. 1개 웹 페이지(또는 명확히 구분되는 주요 화면
  영역)당 1개 Page 클래스를 작성합니다.
- 모든 Page 클래스는 공통 기능을 제공하는 `BasePage`를 상속합니다.
- Page 객체는 WebDriver 인스턴스 1개만 보유하며, 그 외 상태 변수를 최소화합니다.
- Page Layer와 Test Layer의 책임은 4절 기준을 따릅니다.
- 각 Page 클래스는 자신의 화면 전용 Locator를 제공하는 `<PageName>Locators` 클래스를
  상속(mixin)합니다. Locator 정의와 화면 조작 책임을 분리하기 위함이며, 상세 규칙은
  6.2절을 따릅니다.

---

## 3. Project Structure

아래는 목표 구조입니다. 2026-10-13 현재 실제로 존재하는 항목은 `config/`, `conftest.py`,
`pytest.ini`, `requirements.txt`, `scripts/`, `reports/`, `screenshots/`와 CI 워크플로우이며,
`pages/`, `locators/`, `tests/`, `utils/`, `test_data/`는 새 구현에서 필요한 시점에 생성합니다.

```
automation/
├── pages/               # Page Object 클래스 (신규 구현 시 생성)
│   ├── base_page.py
│   └── ...
├── locators/             # 화면별 Locator 전용 클래스(Page 클래스 밖으로 분리, 6.2절) (신규)
│   ├── base_locators.py
│   └── ...
├── tests/                # 테스트 코드 (pytest) (신규)
│   ├── test_<feature>.py
│   └── ...
├── utils/                 # 화면과 무관한 공통 로직 (필요 시 생성)
├── config/                 # 환경 설정(URL, 타임아웃, 로그인 방식 등) — 존재
├── test_data/               # 정적 테스트 데이터(계정 이메일 등, 비밀번호 제외) (필요 시 생성)
├── scripts/                   # 세션 쿠키 캡처, Slack 알림, CI 실패 로컬 재검증 — 존재
├── screenshots/               # 실패 시 스크린샷(git 미추적)
├── reports/                     # pytest-html/JUnit XML 리포트(git 미추적)
├── conftest.py                   # pytest fixture, 로그인, 리포트 TC-ID 매핑 — 존재
├── pytest.ini                     # pytest 설정 — 존재
└── requirements.txt                # Python 의존성 — 존재

docs/                                # 산출물(PRD/TC/Automation Candidate/Roadmap/Automation Guide)
scripts/sheets_sync/                  # 기존 Google Sheet 연동 스크립트(자동화 코드와 별개)
.github/workflows/                      # CI 워크플로우 — 존재(test.yml, 실행 범위는 16절 참고)
```

- `automation/` 하위 구조는 이 프로젝트의 자동화 코드 전용이며, 기존 `scripts/sheets_sync`
  (QA 프로세스 도구 스크립트)와는 목적이 다르므로 혼용하지 않습니다.
- 실제 디렉터리를 만들 때 위 구조와 다르게 조정해야 할 이유가 생기면, 이 문서를 먼저 갱신하고
  사용자 확인을 받은 뒤 반영합니다(CLAUDE.md 7절).

### 3.1 Import 경로 규칙

`automation/pytest.ini`가 저장소 루트가 아닌 `automation/` 디렉터리 안에 위치하고
`automation/` 자체에는 `__init__.py`가 없으므로, pytest를 `automation/`에서 실행하면
`automation/`이 사실상의 루트 패키지 경로가 됩니다. 이전 구현에서 아래 규칙으로 정상 동작함을
확인했으며, 새 구현에서도 첫 테스트 실행 시점에 다시 확인합니다.

- 모든 `automation/` 하위 코드(Page Object, 테스트, utils, config, test_data 등)는
  **`automation.` prefix 없이** `automation/` 자체를 루트로 삼아 import한다.
  - 올바른 예: `from pages.base_page import BasePage`, `from config.settings import BASE_URL`
  - 잘못된 예(실행 시 `ModuleNotFoundError` 발생): `from automation.pages.base_page import BasePage`
- 이 규칙은 `automation/` 하위 코드 사이의 상호 import에만 적용된다. `automation/` 바깥
  코드(`scripts/sheets_sync` 등)에서 `automation/` 코드를 import하는 시나리오는 현재
  범위에 없다.

---

## 4. Page Object / Layer 책임

### 4.1 Page Layer 책임

- 대상 화면의 모든 Locator는 Page 클래스가 아닌 전용 Locators 클래스
  (`locators/<page_name>_locators.py`의 `<PageName>Locators`)에 정의합니다. Page
  클래스는 이 Locators 클래스를 상속(mixin)해 `self.LOCATOR_NAME`으로 그대로
  참조합니다(6.2절 참고).
- 클릭/입력/스크롤 등 화면 조작 메서드를 제공합니다.
- 조회 메서드는 값을 **반환만** 합니다.
- **Assertion을 절대 수행하지 않습니다.**

### 4.2 Test Layer 책임

- Page 객체의 메서드를 호출해 시나리오를 구성합니다.
- 테스트에 필요한 데이터를 준비/정리합니다(11절 참고).
- Page에서 반환받은 값과 기대값을 비교해 **Assertion을 수행**합니다.
- 원칙: Page는 "어떻게 하는가", Test는 "무엇을 검증하는가"만 담당합니다.

```python
# locators/sample_locators.py (예시 — 실제 Locator는 구현 시 5절 절차로 확인)
class SampleLocators:
    KEYWORD_INPUT = (By.CSS_SELECTOR, "input[placeholder='입력란 안내문']")
    RESULT_COUNT = (By.CSS_SELECTOR, ".result-count")


# pages/sample_page.py
class SamplePage(SampleLocators, BasePage):
    def search(self, keyword: str) -> None:
        self.type_text(self.KEYWORD_INPUT, keyword)

    def get_result_count_text(self) -> str:
        return self.get_text(self.RESULT_COUNT)


# tests/test_sample.py
def test_search_with_keyword(driver, sample_page):
    sample_page.search("keyword")
    assert sample_page.get_result_count_text() != ""
```

---

## 5. 실제 페이지 탐색 규칙 (Playwright MCP 기반)

Selenium 코드를 작성하기 전 실제 페이지 구조와 Locator 후보를 조사·검증하는 개발 보조
도구로 **Playwright MCP**를 사용합니다(사용자 확정).

### 5.0 사전 준비 상태

Playwright MCP(`mcp__playwright__browser_navigate`, `browser_snapshot`, `browser_evaluate`)는
`automation-developer-agent.md`의 도구 목록에 이미 등록되어 있습니다. 실제 연결/사용 가능
여부는 자동화 구현에 착수하는 시점에 다시 확인합니다. 서버 설정(설치/등록) 자체는 이 문서의
범위가 아닙니다.

### 5.1 사용 목적

- Playwright MCP는 Selenium 테스트 코드에 사용할 실제 페이지 구조와 Locator 후보를
  조사하고 검증하기 위한 **개발 보조 도구**로 사용합니다.
- 프로덕션 테스트 실행 도구는 **Selenium WebDriver**이며, Playwright MCP를 Selenium
  코드 실행 대신 사용하지 않습니다.

### 5.2 기본 탐색 순서

Selenium 코드를 작성하기 전에 다음 순서로 실제 페이지를 확인합니다.

1. 대상 기능의 Feature PRD(`docs/prd/Feature/prd-{slug}.md`)와 승인된 TC 시나리오를 먼저
   확인합니다.
2. Playwright MCP로 대상 페이지(`https://store.laftel.net/`)에 접근합니다.
3. `browser_snapshot`으로 페이지 구조와 대상 요소를 먼저 확인합니다.
4. snapshot만으로 정보가 부족하면 `browser_evaluate`로 DOM 속성을 확인합니다.
5. 확인한 정보를 기반으로 6절 우선순위에 따라 Selenium Locator를 작성합니다.
6. 작성한 Locator가 실제 대상 요소를 고유하게 식별하는지(동일 조건에 일치하는 요소가
   1개뿐인지) 검증합니다.

### 5.3 browser_evaluate 사용 기준

`browser_evaluate`는 다음 정보가 snapshot에서 충분히 확인되지 않을 때만 사용합니다.

- id, name, role, aria-label, placeholder
- data-testid 등 data-* 속성(실제 존재가 확인되는 경우에 한함)
- 대상 요소의 텍스트
- 상위·하위 DOM 관계
- 동일 조건에 일치하는 요소 개수

**금지**: 페이지 상태를 변경하거나 서비스 데이터를 조작하기 위한 JavaScript 실행(실제 계정
생성/삭제, 주문 시도 등)에는 사용하지 않습니다. Playwright MCP는 오직 **조회·탐색** 목적에만
한정하며, 승인되지 않은 Production 데이터 변경은 CLAUDE.md 11절 원칙을 그대로 따릅니다.

### 5.4 사용자 확인 요청 기준

다음 사유로 Playwright MCP를 이용한 직접 확인이 불가능한 경우에만 사용자에게 스크린샷이나
추가 정보를 요청합니다.

- 로그인 계정이나 권한이 없음
- OTP, 2FA 또는 CAPTCHA가 필요함
- 사내망이나 특정 네트워크 환경이 필요함
- 사용자별 데이터가 있어야 재현 가능함
- MCP 브라우저와 실제 테스트(Selenium) 환경이 다르게 동작함
- 대상 요소나 요구사항이 여러 의미로 해석될 수 있음

단순히 Locator가 제공되지 않았다는 이유만으로 작업을 중단하지 않습니다.

---

## 6. Locator 작성 원칙

### 6.1 우선순위

1. `id` 속성
2. `name` 속성
3. 안정적인 CSS Selector(구조 변경에 덜 민감한 속성 기반)
4. 상대 XPath (텍스트/속성 결합 등 다른 방법으로 고유 식별이 어려울 때만, 최후 수단)

**Full XPath(`/html/body/div[1]/...`)는 절대 금지**합니다 — DOM 구조 변경에 매우 취약해
유지보수가 불가능합니다.

> `store.laftel.net`에 `data-testid`/`data-qa` 같은 테스트 전용 속성이 존재하는지는 아직
> 실측되지 않았습니다. 구현 중 Playwright MCP로 특정 화면을 조사하다 이런 속성이 실제로
> 존재하고 다른 속성보다 더 안정적으로 고유 식별이 가능함을 확인하면, 그 화면에 한해
> 우선순위를 갱신하고(사용자 승인 후) 이 절에 실측 근거를 기록합니다.

### 6.2 정의 위치

모든 Locator는 Page 클래스가 아닌 전용 Locators 클래스에 `UPPER_SNAKE_CASE` 상수로
정의합니다. Locators 클래스는 `locators/` 디렉터리 아래 `<page_name>_locators.py`
파일에 `<PageName>Locators`라는 이름으로 작성하고, 대상 Page 클래스가 이를
상속(mixin)합니다(예: `class SearchPage(SearchLocators, BasePage):`). 메서드 내부에
Locator를 하드코딩하지 않습니다.

파라미터에 따라 값이 달라지는 동적 Locator(인덱스/ID 등이 포함된 XPath)는, `self.driver`나
다른 화면 조작 메서드를 호출하지 않고 `(By.X, "...")` 튜플만 구성해 반환한다면 정적 상수와
동일하게 Locators 클래스의 메서드로 정의합니다. 여러 Locator 조합에 재사용되는 XPath
조각은 By 튜플이 아닌 순수 문자열 상수로 Locators 클래스에 정의할 수 있습니다(예:
`SearchResultLocators.SORT_DIALOG_OPEN`). driver 상호작용이나 반복/조건 로직이 포함된
메서드는 Page 클래스에 남깁니다.

---

## 7. Wait 처리 원칙

- **`time.sleep()` 사용을 금지**합니다. 고정 시간 대기는 테스트를 느리고 불안정하게 만듭니다.
- Selenium의 `WebDriverWait` + `expected_conditions`로 **Explicit Wait**를 기본으로
  사용합니다.
- 반복되는 Wait 로직은 `BasePage`의 공통 메서드로 래핑합니다(예: `wait_and_click`,
  `wait_and_get_text` 등 — 실제 메서드명은 구현 시 확정).

### 7.1 자동화를 방해하는 오버레이/팝업

현재까지 `store.laftel.net`에서 자동화(클릭/입력)를 가로막는 것으로 보고된 제3자 광고
오버레이나 그 밖의 방해성 팝업은 없습니다. 구현 중 유사한 문제(광고, 쿠키 동의 배너, 앱
설치 유도 팝업 등)가 실제로 발견되면, 그 시점에 구체적인 증상·재현 조건·처리 방식을
사용자 승인을 거쳐 이 절에 기록하고 `BasePage`에 공통 방어 로직을 추가합니다.

### 7.2 터치 스와이프 기반 컴포넌트의 자동화 제약 (알려진 도구 한계)

상품상세 이미지 캐러셀 구현 중 발견된 ChromeDriver/Selenium 자체의 제약사항입니다(사이트 결함
아님).

- 별도 화살표 버튼 없이 마우스/터치 드래그로만 전환되는 컴포넌트는 `ActionChains`
  (click_and_hold + move_by_offset + release)로 드래그를 구현해야 합니다.
- **같은 브라우저 세션(페이지를 새로 열지 않은 상태)에서 이런 드래그를 2회 이상 연속
  수행하면 ChromeDriver의 W3C Actions 포인터 위치가 누적 이탈해
  `MoveTargetOutOfBoundsException`이 발생**하는 문제를 확인했습니다. 여러 방식(단계별
  이동, 절대좌표 재설정, 하나의 액션 체인으로 통합)으로 우회를 시도했으나 재현되어,
  ChromeDriver의 알려진 한계로 판단합니다.
- **대응 원칙**: 이런 컴포넌트를 검증하는 각 테스트는 페이지를 새로 연 직후 드래그를
  **1회만** 수행하도록 시나리오를 구성합니다(pytest `driver` fixture가 테스트마다 새
  세션을 생성하므로, 테스트 함수를 분리하면 자연스럽게 만족됩니다).
- 이 제약으로 인해 한 세션 내 2회 이상의 연속 드래그가 구조적으로 필요한 시나리오(예:
  "마지막 사진에서 다음으로 넘기면 첫 번째로 순환"처럼 직전 드래그로 도달한 상태에서
  다시 드래그해야 하는 경우)는 자동화 범위에서 제외하고 수동 확인 대상으로 남깁니다
  (자동화 대상 선정 시 Automation Stability 감점 요인으로 반영).
- 터치 스와이프 기반 캐러셀을 자동화할 때는 항상 이 절의 원칙을 적용합니다.

### 7.3 로그인 플로우의 간헐적 지연

로그인 fixture(`conftest.py`의 `logged_in_driver`)에서 이메일 입력 후 "다음" 버튼이 클릭
가능해지기까지 간헐적으로 기본 `DEFAULT_TIMEOUT`(10초)보다 오래 걸리는 현상을 발견했습니다
(같은 세션에서 로그인을 반복 시도할 때 더 자주 관찰됨 — 클라이언트 측 이메일 검증 API 응답
지연으로 추정, 사이트 결함 여부는 확인되지 않음). 이에 로그인 전용 타임아웃을
`config/settings.py`의 `LOGIN_TIMEOUT`(20초)으로 별도 상향했습니다. 그럼에도 실패가 발생하면
CLAUDE.md 13절에 따라 Test Environment 요인으로 우선 의심하고, 동일 테스트를 무분별하게 반복
재시도하지 않습니다.

### 7.4 브라우저 창 크기와 캐러셀 카드 클릭 가로채기

Chrome 기본 창 크기(약 1200x832)에서는 캐러셀 카드 레이아웃이 좁아져 인접 카드 요소가 클릭을
가로채는(`ElementClickInterceptedException`) 현상을 발견했습니다. 이에
`config/settings.py`의 `WINDOW_SIZE`(1600x1000)를 정의하고 `conftest.py`의 `driver`
fixture에서 `driver.set_window_size()`로 명시적으로 적용했습니다(1절 "일반 데스크톱
창 크기" 결정의 구체적 값으로 확정). 새로 작성하는 `BasePage.click()`에는 클릭이 다른 요소에
가로채이면(예: 토스트 알림) 오버레이가 사라질 때까지 같은 요소에 대해 재시도하는
방어 로직을 둡니다(무한 재시도 아님, `DEFAULT_TIMEOUT` 내에서만 재시도).

전체 테스트를 연달아 실행해 같은 상품의 찜 토글을 짧은 시간에 반복 호출한 경우, 마지막 클릭이
`DEFAULT_TIMEOUT`(10초) 안에 반영되지 않아 실패하는 사례를 1회 관찰했습니다(단독 실행하거나
계정의 찜 상태를 정리한 뒤 재실행하면 정상 통과 — 원인은 특정되지 않았으나 짧은 시간 내 반복
호출에 따른 서버 처리 지연으로 추정). 재현이 잦아지면 그때 원인을 추가로 조사하고 이 절에
갱신합니다.

### 7.5 팝업 텍스트를 요소 등장 직후 읽을 때의 빈 문자열 문제

전체 통합 실행 중 로그인 유도 팝업의 텍스트 조회가 간헐적으로 빈 문자열을 반환하는 현상을
발견했습니다. 팝업 h2 요소가 DOM에 먼저 빈 상태로 나타난 뒤 내용이 뒤늦게 채워지는 경우가
있어, `presence_of_element_located`만으로는 불충분했습니다. 요소 존재 확인 후 텍스트가 실제로
채워질 때까지(`wait_for_text`) 기다린 뒤 읽도록 수정했습니다. 이후 유사하게 "요소는
있지만 내용이 비동기로 채워지는" 텍스트 조회 메서드를 추가할 때도 동일하게
`wait_for_text`로 내용이 채워지길 기다린 뒤 반환하는 패턴을 따릅니다.

### 7.6 비동기 갱신 화면의 Race Condition (장바구니에서 확인된 패턴)

장바구니 흐름 구현 중 아래 문제들을 발견했습니다. 모두 "클릭 직후 즉시 다음 동작을 하면 이전
동작이 아직 반영되지 않은 상태를 읽게 된다"는 공통 원인을 가지므로, 목록·개수·선택 상태가
비동기로 갱신되는 화면을 다룰 때 동일 패턴에 유의합니다.

- **진입 직후 스켈레톤 placeholder**: 화면 진입 직후에는 실제 항목이 렌더링되기 전 회색
  스켈레톤만 존재하는 구간이 있어, 이때 개수를 조회하면 0을 반환합니다. 항목이 1건 이상
  있을 것으로 기대되는 시점에는 실제 항목이 나타날 때까지 대기한 뒤 개수를 조회합니다.
- **API 완료 전 페이지 이동**: "담기" 같은 동작 직후 바로 다른 페이지로 이동하면 API 호출이
  완료되기 전에 네비게이션이 발생해 반영되지 않을 수 있습니다. 완료를 알리는 토스트 등을
  확인한 뒤에 이동합니다.
- **삭제 후 목록 갱신 지연**: 삭제 확인 클릭 직후 개수/빈 상태를 조회하면 삭제 전 값을 읽는
  경우가 있습니다. 목록이 기대 개수로 갱신될 때까지 기다린 뒤 조회합니다.
- **전체선택 체크박스의 기본 상태**: 항목을 추가하면 기본으로 선택된 상태일 수 있어, 전체
  선택을 무조건 클릭하면 오히려 전체 해제가 됩니다. 현재 체크 여부를 먼저 확인한 뒤 필요할
  때만 클릭합니다.

> 참고(알려진 한계): 구 스위트를 연달아 실행할 때 동일 계정으로 담기/삭제 API 호출이 빠르게
> 반복되면 대기가 `DEFAULT_TIMEOUT` 내에 완료되지 못해 간헐적으로 실패하는 사례가 드물게
> 있었습니다(단독 실행 시에는 재현되지 않음). 7.4절, 7.11절과 같은 유형이라 판단해 알려진
> 한계로 기록만 하고 무한 재시도는 하지 않습니다.

### 7.7 로그인 방식 임시 전환 (이메일 → 구글, 이메일 계정 서버측 잠금 추정)

이전 구현 중 `TEST_ACCOUNT_EMAIL` 계정으로 로그인을 매우 여러 차례 반복(디버깅 포함)한 뒤
`laftel.net`이 이메일 로그인 자체를 거부하는 오류("앗, 다시 시도해주세요. 알 수 없는 문제가
발생했습니다.")를 반환하기 시작했습니다. 재시도해도 동일하게 재현되어 서버측 일시적 잠금으로
추정했고, 사용자 요청에 따라 잠금이 풀리기 전까지 별도의 구글 계정으로 로그인하도록 임시
전환했습니다.

- `config/settings.py`의 `LOGIN_METHOD` 상수("google"/"email")로 전환하며,
  이메일 로그인 코드(`conftest.py`의 `_login_with_email`)는 삭제하지 않고 그대로
  보존합니다. 잠금이 해제되면 `LOGIN_METHOD = "email"`로 되돌리기만 하면 됩니다.
- 구글 계정 자격 증명은 기존 라프텔 계정과 별개의 전용 테스트 계정이며,
  `GOOGLE_ACCOUNT_EMAIL`/`GOOGLE_ACCOUNT_PASSWORD`로 `.env`에만 저장합니다
  (11.1절과 동일한 원칙).
- 구글 로그인은 `laftel.net/auth/login`의 "구글로 시작" 버튼을 클릭하면 팝업 창으로
  열리며(`window.open`), 로그인 성공 시 팝업이 자동으로 닫히고 원래 창이
  `laftel.net`으로 리디렉션됩니다. 이후 프로필 선택(`img[alt="profile"]` 클릭)
  단계는 이메일 로그인과 동일합니다.
- **알려진 위험 — 구글의 자동화 브라우저 탐지**: 기본 Selenium Chrome으로는 이메일
  입력 직후 구글이 "브라우저 또는 앱이 안전하지 않을 수 있습니다"로 로그인을
  차단하는 것을 실측으로 확인했습니다. `driver` fixture에
  `excludeSwitches=["enable-automation"]`, `--disable-blink-features=AutomationControlled`
  Chrome 옵션과 CDP로 `navigator.webdriver`를 숨기는 완화 조치를 추가해 안정적으로
  통과했지만, 완전한 우회는 아니므로 향후 다시 차단될 수 있습니다. 차단이
  재현되면 추측성 우회를 시도하지 않고 실패로 보고합니다(CLAUDE.md 13절).
- **신규(첫 이용) 계정 전용 온보딩**: 구글 계정으로 처음 스토어를 방문하면 "스토어
  이용약관 동의" 모달이 뜹니다(기존 이메일 계정은 이미 동의되어 있어 겪지 않았던
  차이). `logged_in_driver`가 로그인 직후 `BASE_URL`을 방문해 모달이 있으면
  자동으로 "동의하고 시작하기"를 클릭하도록 처리했습니다.
- **교훈 — 로딩 스켈레톤을 빈 상태로 오판하지 않기**: 계정 전환 검증 중, 화면 진입 직후
  렌더링 완료를 기다리지 않고 "비어 있음"을 판정하면 스켈레톤 로딩 상태를 "비어 있지 않음"으로
  오판해 이후 단계가 타임아웃되는 결함을 발견했습니다(기존 계정은 세션이 따뜻해 우연히
  재현되지 않았을 뿐). 비어 있음/개수 판정 전에는 "실제 항목 또는 빈 상태 안내문 중 하나가
  나타날 때까지" 대기합니다.

### 7.8 사이트 동작 메모 (구 자동화 구현 중 실측한 내용)

2026-09 구 자동화 구현 중 `store.laftel.net`에서 실측한 동작을 요약한 참고 메모입니다. 사이트가
변경되었을 수 있으므로 **새 Locator/시나리오를 작성할 때 5절 절차로 다시 확인**하며, 이
메모를 근거로 확정하지 않습니다.

**주문(체크아웃)**
- 배송지 "우편번호"/"주소" 입력란은 `readonly`라 카카오 우편번호 검색 모달(iframe 안의
  iframe)을 거치지 않고는 채울 수 없습니다. 모달은 외부 모듈이라 모달 자체는 검증 대상으로
  삼지 않고, 유효한 배송지가 선행 조건일 때만 최소 조작(검색어 입력 → 결과 클릭)으로
  사용합니다(사용자 승인 필요).
- 모달 iframe은 열리는 초기에 재구성되어 `switch_to.frame()`이 `StaleElementReferenceException`
  또는 `NoSuchFrameException`으로 실패할 수 있습니다. 두 예외를 모두 잡아 재시도하는 자체
  헬퍼를 사용합니다(`EC.frame_to_be_available_and_switch_to_it`은 `NoSuchFrameException`만
  재시도).
- 같은 문구의 다이얼로그가 DOM에 숨겨진 채 남아 있을 수 있습니다. 확인 버튼은
  `//div[@role="dialog" and @data-state="open"]//button[...]`처럼 열려 있는 다이얼로그로
  범위를 좁힙니다.
- "구매하기" 클릭 후 나이스페이(PG) 결제창은 동일 입력에도 노출이 간헐적이었습니다(Result
  Determinism 낮음). 실제 PG 호출을 반복하는 것도 부작용 리스크(부하, 이상거래 탐지 등)가 있어
  자동화에 부적합하다고 판단했습니다.
- 계정에 이전 배송지가 저장되어 있으면 체크아웃 화면이 이름/휴대폰/주소를 자동으로 채웁니다
  (브라우저 캐시가 아닌 서버측 상태). "빈 폼" 전제의 시나리오는 이 상태를 고려해야 합니다.

**React 컨트롤드 입력**
- 값이 채워진 React 컨트롤드 `<input>`에 `element.clear()`를 호출하면 DOM 값만 비워지고 React
  상태는 갱신되지 않아, 이후 리렌더링 시 이전 값으로 복원됩니다. `Keys.END` 후 실제 글자 수만큼
  `Keys.BACKSPACE`를 전송하는 방식으로 비웁니다.

**찜(위시리스트)**
- 검색/작품(`/ip/{id}`) 화면에는 무한 스크롤 로딩용 빈 `div[role="status"]`가 토스트보다 먼저
  DOM에 있어, role만으로 토스트를 잡으면 항상 빈 요소가 매칭됩니다. 토스트는
  `div[data-scope="toast"][data-part="root"]`로 구분됩니다. `role` 같은 범용 속성으로 요소를
  특정할 때는 같은 속성을 가진 상시 요소가 없는지 실측합니다.
- 작품 페이지의 첫 번째 `찜하기`/`찜 해제` 버튼은 상품 카드가 아니라 **작품(IP) 자체**의 찜
  버튼입니다(토스트 문구도 "찜한 작품에 추가했어요."). 상품 카드의 찜 버튼은 두 번째부터입니다.
- `/my/wish`의 "작품" 탭 섹션은 개별 상품 찜이 아니라 **작품 자체의 찜 상태**로 노출되며, 섹션
  하트를 눌러도 해제되는 것은 작품 찜뿐 개별 상품 찜은 유지됩니다.
- `/my/wish`는 SPA라 진입 직후에는 목록이 비어 있고 비동기로 채워집니다. 목록에 대상 항목이
  나타날 때까지 기다린 뒤 판정합니다.
- 탭 전환 후 반영까지 약 0.5초 지연이 있고, 비활성 탭의 패널도 DOM에서 제거되지 않고
  남습니다. 로케이터를 활성 패널(`@aria-hidden="false"`)로 범위를 한정하고, "사라짐" 판정은
  대기 후 수행합니다(대기 없이 판정해 결함으로 오탐한 사례가 있었음).
- 편집 모드의 "전체 선택" 체크박스와 선택 개수 텍스트는 DOM에는 정상 존재하나 가시성 기반
  조건(`element_to_be_clickable`, `WebElement.text`)에서만 실패했습니다(원인 미규명). JS 클릭과
  `get_attribute("textContent")`로 우회했습니다.
- 예약구매 상품은 하단 구매 버튼 문구가 "구매하기"/"품절"/"판매종료"가 아니라 "예약구매\n예약
  마감까지 N일 HH:MM" 형태라, 버튼 텍스트 기준 로케이터가 매칭되지 않습니다.

**검색**
- 자동완성은 디바운스/네트워크 지연으로 타이핑 직후 목록이 일시적으로 빈 상태입니다. "이전과
  다르면 통과"가 아니라 "이전과 다르면서 비어 있지 않을 때까지" 대기합니다.
- "총 N개" 같은 숫자 삽입 텍스트는 React가 `총 `/`N`/`개`로 텍스트 노드를 분할합니다.
  `contains(text(), ...)` 대신 요소 전체 문자열을 보는 `contains(., ...)`를 사용합니다.
- 검색은 키워드를 단어 단위로 넓게 매칭해, 상품 제목 전체를 검색해도 원하는 상품이 인기순
  1페이지(20건) 밖으로 밀릴 수 있습니다(결함 아님). 특정 상품을 다루는 TC는 해당 키워드로 실제
  1페이지에 노출되는지 실측 후 사용합니다.
- 검색창에 공백만 입력해도 초기화면의 "인기 작품"/랭킹 섹션은 사라지며, "검색페이지 유지"는
  페이지 이동·에러·결과없음 문구 없이 검색 화면에 머무는 것을 뜻합니다. 입력값에 따라 달라지는
  요소를 "화면 유지" 조건으로 쓸 때는 어떤 요소가 반응하는지 먼저 실측합니다.

### 7.9 conftest.py 구글 로그인 로직 분리

구글 로그인 흐름 중 "구글로 시작 버튼이 이미 보이는 화면에서부터 로그인을 끝까지 완료하는"
부분을 `_complete_google_login(driver)`로 분리하고, `_login_with_google(driver)`는
`driver.get(LOGIN_LANDING_URL)` 후 이 헬퍼를 호출합니다(`logged_in_driver` fixture의 동작은
동일). 로그인 유도 팝업의 "로그인" 버튼도 같은 랜딩 화면(`laftel.net/auth/login`, redirect_url
쿼리만 다름)으로 이동하므로, 로그인 완료 후 리디렉션을 검증하는 테스트는 랜딩 화면 도달
이후 `_complete_google_login()`을 바로 호출해 재사용할 수 있습니다.

### 7.10 동적 요소의 텍스트는 headless에서 `textContent`를 우선 검토

다이얼로그·팝업처럼 동적으로 나타나는 요소의 텍스트를 `WebElement.text`(렌더링 가시성에
의존)로 읽으면 headless 모드에서만 빈 문자열이 반환되는 사례가 있었습니다(로컬 비headless에서는
항상 통과). 이런 요소는 처음부터 `get_attribute("textContent")` 사용을 우선 검토합니다.
`CI=true`(headless) 조건으로 로컬에서 직접 재현해 headless 자체의 문제인지 확인합니다.

### 7.11 전체 스위트 연속 실행 시의 간헐적 타이밍 플레이키 (결론)

구 스위트(113건)를 self-hosted 러너에서 15분 이상 연속 실행했을 때, 서로 다른 테스트 3~4건이
실행마다 다른 조합으로 실패하고 해당 테스트를 단독 실행하면 매번 통과하는 현상이 반복되었습니다.
러너 실행 방식(launchd 백그라운드 서비스 vs foreground) 가설은 검증 후 기각되었고, 로그인/세션과
무관한 **전체 스위트 연속 실행 시의 일반적인 간헐적 타이밍 플레이키**로 결론지었습니다(사용자
확인). 이 프로젝트의 다른 플레이키 사례(로그인 지연 7.3절)와 같은 범주이며, 실패 알림을 받으면
해당 테스트만 재실행해 일시적 현상인지 확인하는 정책(CLAUDE.md 13절)을 적용하고 무한 재시도는
하지 않습니다. 이 확인 과정은 `automation/scripts/verify_ci_failures_locally.sh`(GitHub Actions
실행 ID로 실패한 테스트만 로컬에서 재실행)로 자동화되어 있습니다. 정기 실행 대상 스위트는
실행 시간을 짧게 유지하는 것이 이 유형의 플레이키를 줄이는 데 유리합니다.

### 7.12 실제 구글 로그인 UI가 필요한 테스트는 headless를 적용하지 않음

세션 주입이 아니라 실제 `_complete_google_login()` 로그인 UI를 통과해야 하는 테스트는, CI에서
headless 모드로 실행하면 Google이 "로그인할 수 없음 — 브라우저 또는 앱이 안전하지 않을 수
있습니다"로 차단합니다(한국 로컬 머신이어도 headless라는 이유만으로 차단되며 IP/위치 문제가
아님). 우회를 시도하지 않고, 이런 테스트에만 `@pytest.mark.requires_real_browser` 마커를 붙여
`conftest.py`의 `driver` fixture가 CI에서도 headless를 적용하지 않도록 분기합니다(다른 테스트의
headless 동작은 변경 없음). 새 구현에서 실제 로그인 UI 테스트가 생기면 이 방식을 재사용하며,
없으면 마커와 분기는 정리 대상입니다.

---

## 8. Assertion 원칙

- Assertion은 **Test Layer에서만** 수행합니다(4.1절과 연결).
- pytest의 `assert`를 사용하며, 실패 메시지에 **기대값과 실제값을 모두 포함**합니다.

```python
assert actual_count == expected_count, f"Expected {expected_count}, but got {actual_count}"
```

---

## 9. Fixture 원칙

- WebDriver 생성/종료는 `conftest.py`의 fixture로 관리하며, `yield` 패턴으로 테스트 종료 후
  리소스 정리(`driver.quit()`)를 보장합니다.
- 기본 `scope`는 **`function`**으로 설정해 테스트마다 새 WebDriver를 생성합니다(10절 테스트
  독립성과 직결).
- 자주 쓰이는 Page 객체도 fixture로 제공해 테스트 코드의 반복을 줄입니다.

```python
@pytest.fixture(scope="function")
def driver():
    # 일반 데스크톱 창 크기로 실행 (모바일 에뮬레이션 옵션 없음 — 1절 참고)
    driver = webdriver.Chrome()
    yield driver
    driver.quit()


@pytest.fixture
def login_page(driver):
    return LoginPage(driver)
```

---

## 10. 테스트 독립성

- 각 테스트는 **단독 실행 가능**해야 하며, 다른 테스트의 실행 순서에 의존하지 않습니다.
- 각 테스트는 스스로 필요한 상태(로그인 등)를 셋업합니다.
- 테스트가 생성한 데이터(회원가입으로 만든 계정 등)는 가능한 범위에서 해당 테스트 내에서
  정리합니다(11절 데이터 관리 원칙과 연결).
- 이 원칙은 CLAUDE.md 10절 "Isolated/Reproducible/Idempotent" 원칙을 자동화 코드 수준에서
  구체화한 것입니다.

---

## 11. 테스트 데이터 관리

이 프로젝트는 dev/staging 없이 **Production 단일 환경**입니다. In Scope 범위는 Project PRD를
따르며, 계정을 새로 생성·삭제하는 시나리오는 없습니다. **고정 계정 재사용 방식만 사용합니다.**

### 11.1 고정 계정 재사용 (로그인 상태가 필요한 시나리오)

- 장바구니/찜/주문처럼 "로그인 상태"가 전제 조건인 TC는 사전 준비된 고정 계정을 재사용합니다.
- 계정 **이메일과 비밀번호 모두** 어떤 파일에도 하드코딩하지 않고 `.env`(환경변수)로만
  관리합니다(`TEST_ACCOUNT_EMAIL`, `TEST_ACCOUNT_PASSWORD`, 12절 참고). 계정과 무관한 정적
  테스트 데이터가 필요해지면 그때 `test_data/`를 생성해 사용합니다.
- 이메일 로그인 계정이 서버측 잠금으로 추정되는 문제로 막혀, 별도의 구글 전용 테스트
  계정(`GOOGLE_ACCOUNT_EMAIL`/`GOOGLE_ACCOUNT_PASSWORD`, 역시 `.env`로만 관리)으로
  임시 전환했습니다. `config/settings.py`의 `LOGIN_METHOD` 상수로 전환하며, 상세 배경과
  구현/위험은 7.7절 참고.

### 11.2 주문(결제) 관련 데이터 제약

- Project PRD 6절 In Scope는 "주문(**결제 제외**)"로 한정되어 있습니다. 자동화 코드는 주문/
  결제 화면 진입, 배송지·배송요청사항 입력, 약관 동의까지만 다루고, **실제 결제(PG 결제
  완료)는 어떤 테스트에서도 수행하지 않습니다.** PG 결제창 진입 검증은 노출이 간헐적이고
  반복 호출 자체가 부작용 리스크가 있어 자동화에 부적합했습니다(7.8절 참고).
- 따라서 주문 관련 테스트로 인해 실제 주문 데이터가 생성되는 일은 없는 것으로 판단하지만,
  구현 중 예상과 다른 부작용(예: 결제창 진입만으로 주문이 생성되는 등)이 발견되면 즉시
  중단하고 CLAUDE.md 11절에 따라 사용자에게 보고합니다.

### 11.3 공통 원칙

- 테스트 데이터를 코드에 직접 하드코딩하지 않습니다.
- Production 데이터(실제 사용자 데이터 등)를 생성/수정/삭제하는 작업은 CLAUDE.md 11절에
  따라 사용자의 명시적 승인 없이 수행하지 않습니다.
- 특정 상품·키워드처럼 판매 데이터(재고/판매상태/가격/검색 순위)에 의존하는 테스트 데이터는
  QA가 통제할 수 없어 시간이 지나면 가정이 깨질 수 있습니다. 이런 데이터는 `config/settings.py`
  상수 한곳에 모으고 가정 조건을 주석으로 남기며, 실행 시점에 상태를 재확인합니다. 정기 실행
  대상 TC를 설계할 때는 특정 상품 상태에 덜 의존하도록 전제 조건을 선정합니다.

---

## 12. 환경변수 및 민감정보 관리

- 비밀번호 등 민감정보는 코드에 절대 작성하지 않고 환경변수로 관리합니다
  (`python-dotenv` + `.env`).
- `.env`는 `.gitignore`에 포함해 git에 커밋되지 않도록 합니다(이미 프로젝트
  `.gitignore`에 `.env` 규칙이 존재하며, 자동화 코드용 변수도 동일한 방식을 따릅니다).
- CI(GitHub Actions) 환경에서는 GitHub Secrets로 관리합니다(CLAUDE.md 17절과 동일).
- 로그, 리포트(HTML/JUnit XML), 실패 스크린샷 어디에도 비밀번호 등 민감정보가 노출되지
  않도록 합니다.

---

## 13. Logging

- `print()` 대신 Python 표준 `logging` 모듈을 사용합니다.
- 로그 레벨 기준:
  - `DEBUG`: Locator 탐색, 요소 상태 등 상세 진단 정보
  - `INFO`: 로그인, 페이지 이동, 클릭 등 주요 액션
  - `WARNING`: 재시도, 느린 응답 등
  - `ERROR`: 예외 발생, 요소를 찾지 못함 등
  - `CRITICAL`: 드라이버 크래시 등 심각한 오류
- 비밀번호 등 민감정보는 로그에 마스킹 처리합니다.
- 로그 저장 경로/포맷/로테이션 방식은 실제 구현 시 확정합니다(현재 미정).

---

## 14. 실패 시 Screenshot / Artifact

- pytest hook(`pytest_runtest_makereport`)을 이용해 테스트 **실패 시에만** 자동으로
  스크린샷을 캡처합니다.
- 파일명 규칙: `{테스트_함수명}_{상태}_{YYYY-MM-DD_HH-MM-SS}.png`
- 저장 위치: `automation/screenshots/`(git 미추적)
- 스크린샷에 민감정보(비밀번호 입력값 등)가 노출되지 않도록 주의합니다.
- CI 실행 시 실패 스크린샷과 리포트(pytest-html, JUnit XML)는 GitHub Actions Artifact로
  업로드해 사후 확인이 가능하도록 합니다(16절 CI/CD와 연결, 실제 워크플로우 파일은 별도
  단계에서 작성 — CLAUDE.md 15절).

### 14.1 리포트의 TC-ID 매핑

- 모든 테스트 함수는 docstring 첫 줄에 `TC-<FEATURE>-<3자리>` 형식(예: `TC-CART-001`,
  `TC-PRODUCT-DETAIL-013`)을 명시해야 하며, 뒤에 `" (Negative)"`처럼 부가설명을 붙일 수
  있습니다. 이 형식은 구 TC 네이밍 기준이며, **새 Regression TC의 ID 네이밍이 확정되면
  `conftest.py`의 `TC_ID_PATTERN`과 함께 이 절을 재검토**합니다.
- `conftest.py`의 `pytest_runtest_setup` 훅이 이 docstring에서 정규식(`TC_ID_PATTERN`)으로
  TC-ID를 추출해 `item.user_properties`에 `("tc_id", ...)`로 부착합니다. 이 값은 pytest
  표준 메커니즘을 통해 `results.xml`의 각 `<testcase>`에
  `<properties><property name="tc_id" value="TC-CART-001" /></properties>`로 자동
  기록됩니다.
- `report.html`(pytest-html)에는 같은 값을 `pytest_html_results_table_row`가
  `report.user_properties`에서 재조회해 "TC-ID" 컬럼(`Result | TC-ID | Test | Duration |
  Links` 순)으로 표시합니다. 정규식 추출 로직은 `_extract_tc_id` 한 곳에만 존재하며
  두 리포트가 이를 재사용합니다.
- docstring에 TC-ID가 없거나 패턴이 어긋나는 경우 `"-"`로 표시됩니다(현재는 모든 테스트가
  패턴을 따르므로 발생하지 않지만, 향후 예외 케이스에 대한 안전장치입니다).
- CI Slack 알림(`automation/scripts/notify-ci-slack.sh`)도 동일한 `<properties>`를 읽어
  실패 목록 각 줄에 TC-ID를 표시합니다(예: `` `TC-CART-001` `tests/test_<feature>.py:42` — ...
  ``). `<properties>`가 없는 과거 결과 XML을 넣어도 `"-"`로 표시될 뿐 스크립트가 깨지지
  않습니다.

---

## 15. Exception Handling

- 프로젝트 전역 CLAUDE.md "에러 핸들링 필수" 원칙을 자동화 코드에서는 다음과 같이
  구체화합니다.
- 불필요하게 광범위한 `except Exception:` 처리를 지양하고, Selenium이 실제로 발생시키는
  구체적 예외(`TimeoutException`, `NoSuchElementException` 등)를 명시적으로 처리합니다.
- 예외 발생 시 반드시 로그를 남겨(`logger.error(...)`) 이후 디버깅이 가능하게 합니다.
- 예외를 조용히 삼키지 않습니다(로깅 없이 `pass` 처리 금지).

---

## 16. CI/CD

- GitHub Actions를 사용합니다. 트리거(Push / Cron / workflow_dispatch)별 실행 범위는 새 TC
  설계와 자동화 적합성 평가가 완료된 뒤 결정합니다. 현재 방향(확정 아님)은 다음과 같습니다.
  - Push: 자동화 코드 변경 검증을 위한 Smoke 또는 변경 관련 테스트
  - Cron(정기 실행): 자동화 대상으로 선정된 주요 Regression TC. 목표는 "공개 서비스의 주요
    기능 이상 감지"이며, 자동화 코드 구현과 안정화가 끝난 뒤 활성화
  - workflow_dispatch: 필요 시 수동 실행
- 현재 `test.yml`은 이전 구성(main push 시 전체 `pytest` 실행)이며, 정기 실행(schedule)은
  비활성 상태로 두었습니다. 새 실행 범위가 확정되면 수정하고, 정기 실행은 안정화 이후 사용자 승인을
  받아 활성화합니다.
- 실행 흐름(CLAUDE.md 15절 기준): `트리거(Push/Cron/수동) → GitHub Actions → 자동화 테스트
  실행 → Test Report 생성 → 결과 판정 → Slack Notification`
- **실패 시 Slack 알림에는 어떤 부분(테스트/Feature)에서 실패했는지 알 수 있는 정보를
  포함**합니다. JUnit XML 결과를 파싱해 실패한 테스트 이름과 사유 요약을 메시지에 포함하는
  방식을 사용합니다(1절 리포팅 결정과 연결).
- 이 문서는 CI **운영 원칙**만 정의하며, 실제 GitHub Actions Workflow(YAML) 파일과 Slack
  연동 스크립트는 별도 구현 단계에서 작성합니다(CLAUDE.md 15절과 동일한 범위 제한).
- Slack은 결과 알림 전용이며 Commit/Push 승인 용도로 사용하지 않습니다(CLAUDE.md 16절).

### 16.1 CI 환경 로그인 전략 (세션 주입)

- **테스트 및 CI에서는 구글 OAuth 로그인 UI를 직접 자동화하지 않습니다.** 로그인 화면
  자체를 Selenium으로 조작하는 방식(7.7절의 `_complete_google_login()`)은 로컬 개발
  환경에서만 사용하며, CI(GitHub Actions)에서는 사용하지 않습니다 — CI 환경(매번 다른
  IP/디바이스 지문)에서는 구글의 자동화 브라우저 탐지에 의한 로그인 차단이 로컬보다
  훨씬 자주 발생할 위험이 있기 때문입니다.
- **대신 세션 주입(Session Injection) 방식을 사용합니다.** 로컬에서 기존
  `_complete_google_login()`으로 고정 계정 로그인을 1회 수행해 인증 후 세션 쿠키를
  캡처하고, 이를 GitHub Secret(예: `SESSION_COOKIES_JSON`)으로 저장합니다. CI 실행
  시에는 이 저장된 세션을 브라우저에 주입(`driver.add_cookie()` 등)해 로그인 상태를
  만들며, 구글 로그인 화면 자체는 거치지 않습니다.
- **로컬 개발 환경의 기존 동작은 변경하지 않습니다.** 세션 주입은 CI 환경에서만
  분기되며, 로컬에서는 지금까지와 동일하게 `logged_in_driver`가 직접 구글 로그인을
  수행합니다.
- **세션 만료 시 갱신은 사용자가 수동으로 수행합니다.** 별도의 자동 갱신 워크플로우는
  두지 않으며, 로컬에서 세션을 다시 캡처해 GitHub Secret 값을 수동으로 업데이트하는
  절차를 따릅니다. 캡처한 세션 쿠키는 민감정보이므로 로컬 디스크에 파일로 남기지 않고
  즉시 GitHub Secret 등록에만 사용합니다(12절 환경변수 관리 원칙과 동일하게, CI는
  GitHub Secrets로만 관리하고 로그에 노출하지 않습니다).
- **CI 러너는 GitHub 호스팅이 아닌 한국 소재 self-hosted 러너(로컬 macOS)를
  사용합니다.** CI 실행 실측 결과 `store.laftel.net`이 한국 외 지역 IP를
  차단해("Sorry, this service is only available in South Korea.") GitHub 호스팅
  러너(해외 데이터센터)에서는 사이트 접속 자체가 불가능함을 확인했습니다. 워크플로우의
  `runs-on`은 `[self-hosted, macOS, korea]`이며, 이 러너에는 이미 Python/Chrome이
  설치되어 있어 `actions/setup-python`·`browser-actions/setup-chrome`은 사용하지
  않습니다. 러너는 `~/actions-runner-laftel-store`에 설치되어 있습니다.
- **예외 — 로그인 UI 자체를 검증하는 테스트는 세션 주입이 아닌 실제 구글 로그인을 사용합니다.**
  "로그인 완료 후 리디렉션"처럼 로그인 UI 자체가 대상인 테스트는 세션 주입으로 대체할 수
  없습니다. CI 러너가 로컬 한국 머신이라(해외 클라우드 IP가 아님) 봇 탐지 위험이 로컬 개발
  시와 동일한 수준으로 낮아져, `GOOGLE_ACCOUNT_EMAIL`/`GOOGLE_ACCOUNT_PASSWORD`도 GitHub
  Secret으로 등록해 이런 테스트만 예외적으로 실제 로그인 플로우를 사용합니다(headless 제약은
  7.12절). 이전 구현에서 적용한 방식이며 새 구현에서 필요한지는 TC 확정 후 결정합니다.

### 16.2 세션 쿠키 수동 갱신 런북

`SESSION_COOKIES_JSON`은 만료 시(로그인 필요 테스트들이 한꺼번에 실패하기 시작하는
것으로 관찰됨) 사용자가 아래 절차로 직접 갱신합니다. 자동 갱신 워크플로우는 두지
않습니다(16.1절).

1. 만료 징후 확인: Slack 실패 알림에서 `logged_in_driver` 기반(로그인 필요) 테스트가
   여러 파일에 걸쳐 대거 실패하고, 실패 사유가 로그인 프롬프트 관련 요소를 찾지 못하는
   타임아웃 패턴이면 세션 만료를 의심합니다.
2. `automation/` 디렉터리에서 새 세션을 캡처해 곧바로 GitHub Secret에 덮어쓰기
   등록합니다(파일로 저장하지 않고 파이프로 직접 전달):
   ```bash
   python3 scripts/export_session_cookies.py | gh secret set SESSION_COOKIES_JSON --repo erik042156/laftel-store
   ```
3. `gh secret list --repo erik042156/laftel-store`로 `SESSION_COOKIES_JSON`의
   갱신 시각이 방금 시점으로 바뀌었는지 확인합니다.
4. 임의의 로그인 필요 테스트를 담은 커밋을 Push(또는 재실행)해 CI에서 실제로
   로그인 상태가 정상 반영되는지 확인합니다.
5. 구글 계정 비밀번호 자체를 변경한 경우에는 `GOOGLE_ACCOUNT_EMAIL`/
   `GOOGLE_ACCOUNT_PASSWORD` Secret도 동일한 방식(`gh secret set`)으로 갱신합니다
   (이 두 값은 실제 로그인 UI 테스트 전용, 16.1절 참고).

세션 만료 주기는 아직 확정되지 않았으며(실사용 중 관찰 예정), 만료 시 위 절차로
대응합니다.

### 16.3 self-hosted 러너 운영 참고

- 러너 설치 위치: `~/actions-runner-laftel-store`(Git 저장소 바깥, 별도 디렉터리).
- 상태 확인: `cd ~/actions-runner-laftel-store && ./svc.sh status` 또는
  `gh api repos/erik042156/laftel-store/actions/runners --jq '.runners[]'`.
- 러너를 재시작해야 하면 `./svc.sh stop && ./svc.sh start`를 사용합니다(launchd
  백그라운드 서비스로 등록되어 있어 로그아웃/재부팅 후에도 자동 재시작됩니다).
- 이 머신이 꺼져 있거나 서비스가 중지된 동안 Push된 커밋은, 러너가 다시 온라인이
  될 때까지 GitHub Actions 큐에서 대기합니다(즉시 실행되지 않음).
- 이전 구성은 `test.yml`의 `schedule: cron: "0 12 * * *"`(매일 한국시간 오후 9시, GitHub
  Actions의 schedule은 항상 UTC 기준이라 UTC 당일 12시로 지정)로 push가 없는 날에도 매일
  전체 테스트를 실행했다. **현재 이 schedule은 비활성(주석 처리) 상태**이며, 자동화 대상 선정과
  CI 설정 확정, 안정화 기준 충족, 사용자 승인 이후에만 활성화한다(CLAUDE.md 15·18절). 활성화되면
  이 시각에도 러너가 오프라인일 때 온라인이 될 때까지 대기한다.

---

## 17. Coding Convention

- 1.1절의 "코딩 스타일 예외"에 따라 **PEP8**을 기준으로 합니다.
  - 들여쓰기: 4칸
  - 한 줄 최대 길이: 100자 권장
  - 타입힌트를 함수 파라미터/반환값에 권장(가독성 확보)
- 주석은 프로젝트 전역 CLAUDE.md에 따라 **한국어**로 작성합니다.
- 변수명/함수명은 영어를 사용합니다(전역 CLAUDE.md "변수명/함수명: 영어" 원칙 유지, 표기법만
  1.1절 예외에 따라 snake_case).

---

## 18. Naming Convention

| 대상 | 규칙 | 예시 |
|---|---|---|
| 파일명 | snake_case | `login_page.py`, `test_login.py` |
| 클래스명 | PascalCase | `LoginPage`, `BasePage` |
| Page 객체 클래스 | `Page` 접미사 필수 | `LoginPage` (O), `Login` (X) |
| 메서드명 | snake_case, 동사로 시작 | `click_login_button`, `get_error_message` |
| 테스트 함수명 | `test_` 접두사 | `test_login_with_valid_credentials` |
| 변수명 | snake_case | `search_keyword`, `product_count` |
| 상수(Locator 등) | UPPER_SNAKE_CASE | `LOGIN_BUTTON`, `EMAIL_INPUT` |
| Locators 클래스 | PascalCase + `Locators` 접미사 | `CartLocators`, `SearchLocators` |
| Locators 파일명 | snake_case + `_locators.py` | `cart_locators.py` |

---

## 19. 공통 코드 분리 기준

- **2회 이상 반복**되는 코드는 공통 메서드/함수로 분리합니다(CLAUDE.md 12절 "불필요한 중복
  구현 금지"와 연결).
- **BasePage**: 모든 Page에서 필요한 공통 화면 조작(요소 찾기, 클릭, Wait 래핑 등).
- **utils**: 화면과 무관한 순수 로직(랜덤 데이터 생성, 문자열/날짜 처리 등).
- 특정 Feature 하나에서만 쓰이는 로직을 섣불리 공통화하지 않습니다(과도한 추상화 지양).

---

## 20. 테스트 실행 및 검증

### 20.1 테스트 실행 범위와 시점

테스트를 "언제, 어느 범위까지" 실행할지를 3단계로 구분합니다. 범위를 넓게 잡을수록(특히 전체
통합 실행) 실행 시간이 길고 제3자 광고 등 Test Environment 요인에 따른 불안정성(7.1절, 22절)에
노출될 여지도 커지므로, 아래처럼 시점을 명확히 구분해 불필요한 반복 실행을 피합니다.

1. **코드 작성 단위(Task)마다**: Page Object 메서드나 테스트 함수를 새로 작성/수정할 때마다, 그
   범위에 해당하는 테스트를 즉시 실행해 동작을 검증합니다. 실행 없이 "완료"로 간주하지
   않습니다(CLAUDE.md 13절과 동일).
   ```bash
   # 예시 형식 — 실제 파일/함수명은 구현 시 결정됨(TC ID와 함수명의 대응 관계는 각 테스트
   # 함수의 docstring에 기록). pytest 노드 ID(파일::함수명)로 지정해 그 테스트만 실행한다.
   pytest automation/tests/test_<feature>.py::test_<시나리오를_설명하는_함수명>
   ```
2. **Roadmap의 구현 단위(Phase) 코드 작성 완료 시**: 해당 단위에 포함된 자동화 대상 TC 전체를
   대상으로 pytest를 실행해 PASSED/FAILED/ERROR를 확인합니다. 실행 범위는 **해당 단위의 테스트
   파일로 한정**하며, 다른 단위까지 포함한 전체 실행은 이 시점에 진행하지 않습니다.
   ```bash
   pytest automation/tests/test_<feature>.py --html=automation/reports/report_<phase>.html --junitxml=automation/reports/results_<phase>.xml
   ```
3. **전체 통합 실행**: Roadmap상 모든 구현 단위의 코드 작성이 완료된 뒤, CI 연동 단계 착수 직전에
   **1회만** 진행합니다. 그 이전 개별 단위 완료 시점마다 반복적으로 전체 실행을 수행하지
   않습니다. ("Regression 스위트"의 구성과 정기 실행 범위는 새 TC·자동화 대상 확정 후 별도로
   정의하며, 이 3단계와는 구분합니다.)
   ```bash
   pytest automation/tests/ --html=automation/reports/report_full.html --junitxml=automation/reports/results_full.xml
   ```

- 테스트 실패 시 원인을 CLAUDE.md 13절의 4가지 범주(Automation Code / Test Data / Test
  Environment / 실제 Product 문제) 중 하나로 구분하려고 시도하며, 원인이 불명확하면 추측으로
  결론 내리지 않고 사용자에게 보고합니다.
- 실패를 회피하기 위해 무한/반복적으로 재시도하지 않습니다.

---

## 21. 코드 작성 후 Self Review 체크리스트

코드 작성을 완료로 보고하기 전에 다음을 자체 점검합니다.

- [ ] `time.sleep()`을 사용하지 않았는가? (Explicit Wait 사용)
- [ ] Full XPath를 사용하지 않았는가?
- [ ] 모든 Locator가 Page 클래스가 아닌 전용 `<PageName>Locators` 클래스에 정의되어
      있는가?
- [ ] Page 클래스가 대응하는 Locators 클래스를 상속(mixin)하고 있는가?
- [ ] Page Layer에 Assertion이 없는가?
- [ ] 모든 Page 클래스가 `BasePage`를 상속하는가?
- [ ] 각 테스트가 다른 테스트 실행 순서에 의존하지 않는가?
- [ ] 계정 정보/비밀번호가 코드에 하드코딩되지 않았는가?
- [ ] `print()` 대신 `logging`을 사용했는가?
- [ ] 예외를 광범위하게 처리하지 않고 구체적으로 처리·로깅했는가?
- [ ] 파일명(snake_case)/클래스명(PascalCase, `~Page` 접미사)/함수명(snake_case,
      동사 시작)/테스트 함수명(`test_` 접두사) 규칙을 지켰는가?
- [ ] 4칸 들여쓰기를 사용했는가?
- [ ] 코드 작성 후 실제로 pytest를 실행해 결과(PASSED/FAILED/ERROR)를 확인했는가?
- [ ] 실패 시 스크린샷이 저장되었는가?
- [ ] (Locator를 새로 작성한 경우) 5절 절차에 따라 Playwright MCP로 실제 페이지 구조를
      확인하고 Locator의 고유성을 검증했는가?

---

## 22. 알려진 Production 사이트 결함 (Known Site Defects)

이 절은 자동화 코드/Locator/Assertion 자체는 정상 동작하지만, `store.laftel.net`
Production 사이트 쪽 결함으로 인해 테스트가 실패(또는 실패할 수 있는)하는 사례를
기록합니다. CLAUDE.md 13절 "실제 Product 문제" 범주로 분류된 사례가 대상입니다.

**현재 이 문서에 등록된 사례는 없습니다.** 새 자동화 구현 중 이런 사례가 발견되면 22.1절부터
이어서 기록합니다.

> 참고: 구 TC 문서(`docs/tc/search.md`, 현재는 초기화되어 저장소에 없음)에는 TC 작성 단계에서
> 발견된 결함 의심 항목(DEFECT-SEARCH-001, 와일드카드성 특수문자 검색 시 결과 없음 화면 미노출)이
> 있었으나, 자동화 구현 중 실제로 마주친 사례가 아니어서 이 절에는 등록하지 않았습니다. 새 TC
> 설계 시 해당 시나리오를 다시 다루게 되면 그 시점에 재확인합니다.

---

## 변경 이력

| 날짜 | 변경 사유 | 상태 |
|---|---|---|
| 2026-09-05 ~ 2026-09-14 | 구 Feature 기반 자동화(cart/order/product-detail/search/wishlist, 113건) 구현·운영 기간의 이력을 압축 기록. 기술 스택(Python/Selenium/pytest/POM) 확정, Python 코드 스타일 예외(1.1절), Locators 분리 구조(2·4·6절), 로그인 방식 전환(7.7절), CI 세션 주입·self-hosted 한국 러너·정기 실행(16절), 리포트 TC-ID 매핑(14.1절)을 이 기간에 확정했다. 구 코드에 종속된 상세 실측 기록은 7.8절 "사이트 동작 메모"로 요약했다. | 승인완료 |
| 2026-10-13 | 프로젝트 목표 재정의("리스크 기반 핵심 Regression TC를 CI에서 정기 실행해 공개 서비스의 주요 기능 이상 감지")에 따라 기존 테스트·Page Object·Locator 코드와 ROADMAP.md를 삭제하고, 이 문서에서 구 코드·구 TC 종속 서술을 정리. 0·0.1·3·3.1절 현재 상태 반영, 7.2~7.6절 일반화, 7.8~7.20절을 7.8절 사이트 동작 메모로 요약(이하 절 번호 재정렬), 11·14.1·16·20.1·22절의 구 TC/Phase 언급 정리. 규칙(1~2, 4~6, 8~10, 12~13, 15, 17~19, 21절)은 변경 없음 (사용자 승인). | 승인완료 |