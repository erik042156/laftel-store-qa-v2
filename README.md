# Laftel Store QA Automation

[라프텔 스토어](https://store.laftel.net/)(애니메이션 굿즈 커머스)를 대상으로, 
요구사항 분석→ Test Case 설계 → 자동화 대상 선정 → E2E 구현 → CI 결과 확인까지 이어지는 QA Automation
Workflow를 구축한 개인 포트폴리오 프로젝트입니다.

단순히 AI를 이용해 결과물을 생성하는 것이 아니라, 반복적인 QA 작업은 AI가 보조하고
요구사항 해석, Test Coverage, 자동화 대상 선정 등 QA 판단이 필요한 단계에는 QA Engineer의 승인을
유지하는 구조를 목표로 설계했습니다. 

전체 운영 원칙은 [`CLAUDE.md`](./CLAUDE.md)를 따릅니다.

## Project Summary

- **Scope**: 라프텔 스토어(애니메이션 굿즈 커머스) 5개 기능(검색/상품상세/찜/카트/주문) 대상 QA Automation
- **Test Coverage**: 전체 152 TC 중 113 TC 자동화 (자세히: 6절)
- **Automation**: Python/Selenium/pytest/POM 기반 E2E 구조 (자세히: 5, 7절)
- **CI**: GitHub Actions self-hosted runner, main Push + 매일 KST 21시 스케줄 (자세히: 8절)
- **Reporting**: pytest-html/JUnit XML + Slack 알림 (자세히: 8절)
- **추적성**: PRD → TC → 자동화 코드 → 실행 결과까지 TC-ID 기반 추적 (자세히: 13절)

---

1. Project Goal
2. Requirements
3. QA Workflow
4. AI / QA Engineer 역할
5. Automation Strategy
6. Test Coverage
7. Architecture
8. CI & Reporting
9. Technical Challenges
10. Output
11. Project Structure
12. Installation / How to Run
13. Documents

---

## 1. Project Goal

### 목표

반복적인 QA업무에 AI를 활용하되,  
요구사항 분석이나 Test Case 최종 승인, 자동화 대상 선정등 같이 QA 판단이 필요한 단계는 QA가 직접 검토하는 Workflow를 설계하는 것을 목표로 했습니다.

### 해결하고자 한 사항

- 요구사항 → TC → 자동화 코드 사이의 추적성 부족
- 반복적인 Test Case 및 자동화 코드 작성 비용
- 자동화 대상 선정 기준이 불명확해지는 문제
- AI가 생성한 결과를 검증 없이 사용하는 위험
- 테스트 실행 및 결과 확인의 반복 작업

### My Contribution
본 프로젝트는 개인 QA 포트폴리오로, 전체 QA Workflow를 직접 설계하고 AI를 보조 도구로 활용하여 구축했습니다.  

- 요구사항 → TC → 자동화 대상 선정 → E2E → CI/Report로 이어지는 QA Workflow 설계
- 공개 서비스 분석을 기반으로 프로젝트용 요구사항 작성 및 Test Case 검토·확정
- 자동화 대상 선정 기준 정의 및 최종 자동화 대상 결정
- Python/Selenium/pytest/POM 기반 E2E 자동화 구조 설계 및 구현
- GitHub Actions 기반 Regression 실행 및 Report/Slack 결과 확인 구조 구성
- Claude Code Agent/Skill의 역할과 QA 승인 지점 설계


## 2. Requirements

본 프로젝트는 라프텔의 실제 내부 기획서(SB)에 접근할 수 없는 개인 포트폴리오 프로젝트입니다.  
따라서 공개된 범위 내에서 확인 가능한 기능과 동작을 기반으로 자동화 프로젝트 수행을 위한 PRD를 별도로 작성했습니다.  
이 프로젝트의 PRD는 실제 라프텔의 내부 요구사항 문서가 아니라, 
**QA Workflow를 검증하기 위한 요구사항 입력값**으로 사용했습니다.

**현재 포트폴리오**

```
서비스 기능 확인 → 프로젝트용 PRD 작성 → Test Case 생성 → QA 검토/승인 → 자동화 대상 선정 → E2E 자동화 구현
```

**실제 업무 적용 방향**

별도의 PRD를 임의로 생성하는 것이 아닌, 
실제 기획서(SB)·정책서·요구사항 문서를 사용하는 것을 전제로 합니다.

```
기획서(SB)/정책서/요구사항 → Claude Code 기반 요구사항 분석 → Test Case 초안 생성
  → QA Engineer 검토 → Test Case 확정 → 자동화 대상 선정 → E2E 자동화 구현
```

요구사항에 정의되지 않은 정책이나 Expected Result는 AI가 임의로 결정하지 않고 "확인 필요사항"으로 분류하여,  
QA Engineer의 검토 및 기획 Q&A를 거친 후 TC에 반영하는 방향을 지향합니다.

## 3. QA Workflow

```
Requirements (PRD)
      ↓
TC Draft (Test Case 초안)
      ↓
QA Review / TC 확정 
      ↓
자동화 대상 선정 
      ↓
QA Decision (자동화 대상 선정 승인)
      ↓
Automation (E2E 구현)
      ↓
CI (GitHub Actions 실행 → Report → Slack)
```

각 화살표 이전 단계는 사람의 승인을 거쳐야 다음 단계로 넘어갑니다  
(4절 AI / QA Engineer 역할,[`CLAUDE.md`](./CLAUDE.md) 18절 User Approval 원칙).  
세부 흐름은 `CLAUDE.md` 3절을 따릅니다.

## 4. AI / QA Engineer 역할

AI는 QA Engineer의 판단을 대체하는 것이 아니라,  
반복 작업을 줄이고 QA Engineer가 Risk와 품질 판단에 집중할 수 있도록 보조하는 역할로 사용합니다.

| QA 단계 | AI / Automation | QA Engineer |
|---|---|---|
| 요구사항 분석 | 문서 분석/구조화 | 요구사항 해석/누락 검토 |
| TC 설계 | TC 초안 생성 | TC 검토 및 최종 승인 |
| 정책 모호성 | 확인 필요 항목 식별 | 기획 Q&A/정책 확정 |
| 자동화 선정 | 후보 분석 | Risk/ROI 기반 최종 선정 |
| 구현 | 코드 생성 보조 | 구조/Assertion/Locator 검토 |
| 실행 | CI 자동 실행 | 실패 원인 분석 |
| 결과 | Report/Slack 전달 | 품질 판단 |

## 5. Automation Strategy

**자동화 우선순위**

- 핵심 사용자 Flow
- Regression 영향도가 높은 기능
- Expected Result가 명확한 TC
- 안정적으로 재현 가능한 TC

**Manual 유지**

- UI/UX의 주관적 판단이 필요한 영역
- 외부 시스템 의존성이 지나치게 높은 TC
- 변경 빈도가 높아 유지보수 비용이 큰 영역 (추정)

**세부 평가 기준**

- Automation Score 평가 기준 6개 
  - Business Criticality  
  - Regression Frequency  
  - Automation Stability  
  - Result Determinism  
  - Manual Test Cost  
  - Maintenance Cost  

- 참고 : [`automation-candidate` Skill](./.claude/skills/automation-candidate/)  

- TC별 실제 평가 결과와 최종 QA Decision은
[`docs/tc/automation-candidates/`](./docs/tc/automation-candidates/)에서 확인할 수 있습니다.

## 6. Test Coverage

| Feature | TC | Automated | 주요 검증 |
|---|---|---|---|
| 검색 | 29 | 23 | 자동완성/검색 결과/최근 검색 |
| 상품 상세 | 46 | 35 | 상품 정보/이미지 슬라이더/옵션 선택 |
| 찜 | 33 | 28 | 찜 추가·삭제/로그인 유도 |
| 카트 | 23 | 16 | 담기/수량 변경/결제 금액 합산 |
| 주문 | 21 | 11 | 배송지 입력/약관 동의/결제 진입 |
| **합계** | **152** | **113** | |

- **TC**: `docs/tc/*.md`에 정의된, 자동화 대상 선정 이전 전체 Test Case 개수
- **Automated**: 사용자 승인을 거쳐 자동화 대상으로 확정되어 실제 구현된 E2E Test 개수
  (`automation/tests/*.py`)
- 나머지(TC − Automated)는 "5. Automation Strategy"의 Manual 유지 기준 또는 외부 연동
  의존성 등의 사유로 Hold/Rejected 처리된 TC이며,  
  TC별 사유는 `docs/tc/automation-candidates/*.md`에서 확인할 수 있습니다.

## 7. Architecture

- **Language**: Python 3.9
- **E2E Framework**: Selenium 4
- **Test Runner**: pytest + pytest-html(HTML/JUnit XML 리포트)
- **설계 패턴**: Page Object Model — 화면 1개당 Page 객체 1개(`automation/pages/`), 로케이터는
  전용 Locators 클래스(`automation/locators/`)로 분리해 Page가 상속(mixin)
- **AI 워크플로우**: Claude Code 기반 Sub Agent/Skill(`.claude/agents/`, `.claude/skills/`) —
  PRD 작성, TC 생성, 자동화 대상 선정, Roadmap 작성, 자동화 코드 구현을 각각 단일 책임의
  Agent/Skill로 분리해 역할이 서로 침범하지 않도록 구성([`CLAUDE.md`](./CLAUDE.md) 6절)

## 8. CI & Reporting

```
Code Push
    ↓
GitHub Actions
    ↓
pytest
    ↓
E2E Test
    ↓
HTML Report
    ↓
Artifact
    ↓
Slack Notification
```

**목적**
> - 반복적으로 수행하는 Regression 테스트를 자동화하고 정해진 시점에 CI에서 실행해 수동 수행 비용을 줄인다
> - 업무 종료 후 야간에 Regression을 실행해, 다음날 업무 시작 전 결과를 확인할 수 있게 한다.

- **GitHub Actions**: `main` 브랜치 Push 시 자동 실행 + 매일 한국시간(KST) 오후 9시 스케줄
  실행(`.github/workflows/test.yml`)
- **Self-hosted Runner**: `store.laftel.net`이 한국 외 지역 IP를 차단해 GitHub 호스팅
  러너로는 접속 자체가 불가능하므로, self-hosted 러너(macOS)를 사용
- **Report**: 실행마다 pytest-html(`report.html`)/JUnit XML(`results.xml`)을 생성하며,
  테스트 함수별 TC-ID를 리포트에 함께 기록해 결과와 Test Case를 바로 매핑할 수 있게 함
- **Artifact**: 리포트(`reports/`)와 실패 스크린샷(`screenshots/`)을 GitHub Actions
  Artifact로 업로드해 사후 확인이 가능하도록 함
- **Slack Notification**: 성공/실패 여부와 실패 시 TC-ID·테스트 파일·실패 사유를 Slack으로
  전달(Commit/Push 승인 용도로는 사용하지 않음, [`CLAUDE.md`](./CLAUDE.md) 16절)

CI가 실패했을 때 실제 문제인지 알려진 일시적 타이밍 이슈("9. Technical Challenges" 참고)인지
빠르게 판별하려면:

```bash
bash automation/scripts/verify_ci_failures_locally.sh [RUN_ID]   # 생략 시 최신 실행
```

## 9. Challenges

### Challenge 1. Google OAuth 인증과 CI 환경

- **문제**: 
  Google OAuth 인증 -> 자동화 브라우저 및 CI 환경에서 보안 정책(자동화 브라우저 탐지) -> 안정적인 E2E 수행이 어려움 존재

  **판단**:
  - Google 로그인 자체를 매 Regression마다 반복 자동화하는 것보다, 인증 이후의 서비스 기능을 안정적으로 검증하는 것이 현재 프로젝트의 자동화 목적에 더 적합하다고 판단
  - 다만 로그인 UI 자체를 검증하는 TC까지 제외하면 로그인 기능의 검증 범위가 사라지기 때문에, 인증 세션을 사용하는 테스트와 실제 로그인 UI를 검증하는 테스트 분리

- **해결**: 
  1. 로컬에서 정상 로그인 후 인증 Session/Cookie 확보
  2. 인증 정보를 GitHub Secret으로 관리
  3. CI 실행 시 Session/Cookie를 주입하여 인증 상태 구성
  4. 로그인 UI 자체를 검증하는 2개 TC는 실제 브라우저 로그인을 유지

- **결과**: 
  - Google OAuth 제약이 있는 환경에서도 인증 이후 주요 E2E Regression을 CI에서 반복 실행할 수 있도록 구성
  - 로그인 기능 자체에 대한 UI 검증 유지

- 구글 로그인 세션 쿠키 캡쳐 : (`automation/scripts/export_session_cookies.py`) 
- GitHub Secret : (`SESSION_COOKIES_JSON`)
- CI에 쿠키 저장 : (`conftest.py`의`_login_with_session_cookies`)


### Challenge 2. CI Runner의 서비스 접근 제한

- **문제**: 
  GitHub-hosted runner에서 Laftel Store에 접근할 경우 지역 제한으로 인해 테스트 대상 서비스에 정상적 접근 불가

- **판단**: 
  - 실행 환경의 네트워크 위치에 따른 문제 (테스트 코드 자체의 실패 아님 )
  - 실제 서비스에 접근 가능한 환경에서 CI를 실행하는 것으로 판단

- **해결**:
  - 국내 네트워크 환경의 self-hosted macOS runner 구성
  - 기존 pytest E2E 실행 구조는 유지, Runner 환경 변경
  - 정기 Regression 실행이 가능하도록 GitHub Actions Workflow 구성

- **결과**: 서비스 접근 조건을 충족하면서 기존 E2E Test를 변경하지 않고 CI Regression 환경을 유지

### Challenge 3. 장시간 E2E Suite의 간헐적 실패 

- **문제**: 
  전체 E2E Suite가 장시간 실행되는 과정에서 일부 테스트가 간헐적으로 실패하는 현상이 발생

- **판단**:
  - 단일 테스트 및 로컬환경에서는 재현되지 않음
  - 기능 결함과 자동화 Timing Issue를 구분할 수 있는 재현 절차가 필요

- **해결**:
  - 실패 테스트를 로컬에서 다시 실행할 수 있는 검증 Script 구성
  - Screenshot 및 Report를 통해 실패 시점의 상태 확인
  - 재실행 결과를 기반으로 기능 결함과 자동화 불안정성을 구분

- **결과**: 
  CI 실패 발생 시 로컬 재현과 Screenshot/Report를 통해 기능 결함과 자동화 불안정성을 구분할 수 있는 검증 절차 마련

- 이슈 발견 경위 및 근거 :  [`AUTOMATION_GUIDE.md`](./docs/automation/AUTOMATION_GUIDE.md) - 7.22·7.23·16절

## 10. Output

- 요구사항 → TC → 자동화 구현으로 이어지는 Claude Code Agent/Skill 기반 QA Workflow 구축
- 전체 152개 TC 중 113개 E2E 자동화
- TC-ID ↔ 자동화 코드 ↔ 테스트 결과 추적 구조 구성
- Selenium + pytest + POM 기반 자동화 Framework 구축
- GitHub Actions 기반 정기 Regression 실행
- HTML Report / 실패 Screenshot / Slack 결과 알림 구성

---

## 11. Project Structure

```
laftel-store/
├── CLAUDE.md              # 최상위 운영 원칙(Agent/Skill 공통 규칙)
├── docs/                  # PRD, TC, Roadmap, 자동화 가이드 (13. Documents 참고)
├── .claude/
│   ├── agents/            # Sub Agent 정의
│   └── skills/            # Skill 정의
├── .github/workflows/     # CI 워크플로우(test.yml)
├── scripts/
│   └── sheets_sync/       # 승인된 TC·자동화 대상 선정 결과를 Google Sheet에 동기화하는 CLI
└── automation/            # 자동화 코드 (Selenium + pytest + POM)
    ├── conftest.py        # driver / logged_in_driver 등 공용 fixture, TC-ID 리포트 매핑
    ├── pytest.ini
    ├── requirements.txt
    ├── config/            # BASE_URL, 테스트 상품 ID 등 실측 상수
    ├── pages/             # Page Object (화면 1개당 파일 1개)
    ├── locators/          # 화면별 Locator 전용 클래스, Page가 상속(mixin)
    ├── tests/             # Feature별 테스트 (TC ID를 docstring에 명시)
    ├── scripts/            # 세션 쿠키 캡처, Slack 알림, CI 실패 로컬 재검증 스크립트
    ├── reports/            # pytest-html / JUnit XML 결과 (git 미포함)
    └── screenshots/        # 실패 시 자동 캡처 (git 미포함)
```

## 12. Installation / How to Run

### 사전 준비물

- Python 3.9 이상 (검증 환경: 3.9.6)
- Google Chrome — `selenium==4.15.2`가 Selenium Manager로 버전에 맞는 chromedriver를
  자동 설치하므로 chromedriver를 별도로 설치할 필요는 없습니다.
- 한국 네트워크 환경 — `store.laftel.net`이 한국 외 IP를 차단하므로 로컬 실행도
  한국에서 접속 가능한 환경이어야 합니다.

### 설치 및 환경변수 설정

```bash
cd automation
pip install -r requirements.txt
cp .env.example .env
```

`.env`에 값을 채웁니다(`automation/.env.example` 참고, 파일은 `.gitignore`에 포함되어
커밋되지 않습니다):

| 변수 | 용도 |
|---|---|
| `GOOGLE_ACCOUNT_EMAIL` / `GOOGLE_ACCOUNT_PASSWORD` | 구글 로그인 계정. `config/settings.py`의 `LOGIN_METHOD`가 기본값 `"google"`이라 사실상 필수입니다. |
| `TEST_ACCOUNT_EMAIL` / `TEST_ACCOUNT_PASSWORD` | 이메일 로그인 계정. `LOGIN_METHOD`를 `"email"`로 바꿀 때만 사용됩니다. |

### 실행

```bash
python3 -m pytest -v                                                            # 전체 113개
python3 -m pytest tests/test_cart.py -v                                         # 파일 단위
python3 -m pytest tests/test_cart.py::test_empty_cart_shows_empty_message -v    # 단일 테스트
python3 -m pytest -k "wish" -v                                                  # 이름 패턴 매칭
```

로컬 실행은 기본적으로 headless가 아니라 Chrome 창이 실제로 뜹니다(`conftest.py`의
`driver` fixture가 `CI` 환경변수 유무로 headless 여부를 분기하며, CI에서만 headless를
적용합니다). `@pytest.mark.requires_real_browser`가 붙은 테스트(TC-WISHLIST-031/032)는
실제 구글 로그인 화면을 그대로 통과해야 하므로 로컬 환경에서도 별도 설정 없이 동일하게
동작합니다.

### 실행 결과 확인

위 명령 중 어떤 방식으로 실행하든(`pytest.ini`의 `addopts`가 항상 적용되므로 별도
옵션을 주지 않아도) 실행이 끝나면 아래 파일이 자동으로 생성/갱신됩니다.

- HTML 리포트: `automation/reports/report.html` — 결과 테이블에 TC-ID 컬럼 포함
- JUnit XML 리포트: `automation/reports/results.xml` (CI의 Slack 알림이 파싱하는 것과
  동일한 형식, `<properties>`에 `tc_id` 포함)
- 실패 시 자동 저장되는 스크린샷: `automation/screenshots/`

셋 다 `.gitignore`에 포함되어 커밋되지 않습니다. Phase별로 리포트 파일명을 따로 남기고
싶다면 `--html=reports/report_phase5.html`처럼 직접 지정하면 기본값 대신 그 이름으로
저장됩니다.

### 문제가 생겼을 때

- `KeyError` 등 로그인 계정 관련 에러가 나면 `.env` 값 누락·오타를 먼저 확인하세요.
- 특정 테스트가 간헐적으로만 실패하면 [`AUTOMATION_GUIDE.md`](./docs/automation/AUTOMATION_GUIDE.md)
  7절(발견된 이슈)과 7.22절(전체 스위트 장시간 실행 시 타이밍 플레이키)을 참고하세요.

## 13. Documents

| 구분 | 위치 | 비고 |
|---|---|---|
| Project PRD | `docs/prd/project-prd.md` | 서비스 개요, 대상 범위 |
| Feature PRD | `docs/prd/Feature/prd-*.md` | 상품상세/카트/주문/찜/검색 |
| Test Case | `docs/tc/*.md` | Feature별 TC, Google Spreadsheet와 동기화 |
| 자동화 대상 선정 | `docs/tc/automation-candidates/*.md` | QA Decision(Approved/Hold/Rejected) 근거 |
| Roadmap | `docs/roadmap/ROADMAP.md` | Phase별 구현 순서, 승인됨 |
| 자동화 컨벤션 | `docs/automation/AUTOMATION_GUIDE.md` | Selenium/pytest 컨벤션, 발견된 이슈·해결 이력 |

각 문서는 상단에 `상태: 승인완료` 메타데이터와 하단 변경 이력 표를 가지며, 승인된 상위
문서는 후속 단계에서 임의로 수정하지 않습니다([`CLAUDE.md`](./CLAUDE.md) 7절).

`.claude/agents/`, `.claude/skills/`에는 PRD 작성·TC 작성·자동화 대상 선정·Roadmap
작성·자동화 코드 구현을 담당하는 전용 Agent/Skill이 정의되어 있으며, 각각 단일 책임만
가지고 서로의 역할을 침범하지 않습니다([`CLAUDE.md`](./CLAUDE.md) 6절).
