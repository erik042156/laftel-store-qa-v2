# CLAUDE.md

이 문서는 `qa-process` 프로젝트에서 Claude Code, 그리고 향후 생성될 모든 Sub Agent / Skill이
공통으로 따라야 하는 최상위 지침입니다. 하위 Agent/Skill의 지침은 이 문서와 충돌할 수 없습니다.

---

## 1. Project Overview

Claude Code를 활용하여 요구사항 정의부터 CI 결과 알림까지 QA 프로세스 전체를
사람의 승인 지점을 유지한 채 자동화하는 프로젝트입니다.
특히 리스크 기반으로 선정한 핵심 Regression 테스트를 CI에서 정기 실행해, 공개 서비스의 주요 기능
이상을 지속적으로 감지하는 QA 자동화 체계를 구축하는 것을 핵심 목표로 합니다.

## 2. Project Goals

- 반복적인 QA 작업(TC 작성, 자동화 코드 구현, 테스트 실행, 리포팅)의 자동화
- 요구사항 → 산출물 → 코드 → 실행 결과 간의 추적성 확보
- 중요한 의사결정 지점(자동화 대상 선정, Commit, Push)에서 사용자 통제권 유지
- Sub Agent/Skill이 늘어나도 일관된 규칙 아래 동작하는 구조 확립
- 리스크 기반으로 선정한 핵심 Regression 테스트를 CI에서 정기 실행하여, 공개 서비스의 주요 기능
  이상을 지속적으로 감지
- 자동화 코드 변경 시 정상 동작과 회귀를 검증하고, 실패 분석 및 Quality Reporting 체계를 유지

## 3. QA Automation Workflow

아래 흐름은 프로젝트의 전체 그림을 설명하기 위한 것이며, 목록의 순서 번호는
**설명 순서일 뿐 다른 섹션에서 참조하는 식별자로 사용하지 않습니다.**
승인이 필요한 작업은 번호가 아니라 [18. User Approval 원칙]에 정의된 **작업 종류** 기준으로 판단합니다.

1. 요구사항을 기반으로 PRD 작성
2. 사용자가 Feature Risk Matrix를 Google Sheet에 직접 작성 (AI 비관여)
3. 사용자가 Project QA Strategy를 Google Sheet에 직접 작성 (AI 비관여)
4. 승인된 PRD와 사용자가 작성한 Feature Risk Matrix/Project QA Strategy를 근거로 전체 기능
   Test Case 초안 생성
5. 사용자가 Test Case를 검토하고 승인
6. 사용자가 Google Sheet의 "Regression 여부" 열에 O/X를 입력해 Regression 범위 지정 (AI 비관여)
7. 사용자 승인 후 "O"로 지정된 TC만으로 Regression Testcase 시트를 새로 생성
8. 사용자가 요청하면 AI가 Regression TC 중에서 자동화 대상을 추천하고, 사용자가 검토해 최종 선정
   *(사용자 승인 필요)*
9. 확정된 자동화 대상을 기반으로 개발 Roadmap 신규 작성
10. Roadmap을 기반으로 테스트 자동화 코드 구현
11. 자동화 테스트 실행 및 결과 검증
12. 코드 리뷰
13. 사용자 승인 후 Git Commit *(사용자 승인 필요)*
14. 사용자 승인 후 Git Push *(사용자 승인 필요)*
15. 자동화 코드 구현·안정화 완료 후 GitHub Actions 기반 CI 실행(정기 실행 및 코드 변경 검증)
16. CI 테스트 성공/실패 결과를 Slack으로 알림하고, 실패 분석 및 Quality Reporting 수행

Feature Risk Matrix와 Project QA Strategy는 AI가 생성·수정하지 않는 산출물입니다. 사용자가
Google Sheet에 직접 작성하며, TC 생성 Agent는 이를 읽기 전용 참고자료로만 사용합니다.
Google Sheet의 "Regression 여부" 열도 사용자가 직접 입력하며, AI는 이 열에 값을 쓰지 않습니다.

**Regression TC**는 전체 기능 TC 중 사용자가 Google Sheet의 "Regression 여부" 열에 "O"로
지정한 TC를 말합니다. **정기 실행 대상**은 이 중 사용자가 최종 선정한 자동화 대상입니다.

## 4. Directory Structure

프로젝트 구조의 기준은 아래와 같습니다.

```
/docs           # PRD, TC, Roadmap 등 산출물 문서
/automation     # 테스트 자동화 코드 (현재 공통 기반만 존재, 테스트·POM 코드는 신규 구현 예정)
/.claude/agents # Sub Agent 정의
/.claude/skills # Skill 정의
/.github/workflows # CI 워크플로우 (생성됨)
```

세부 하위 구조(프레임워크별 폴더 구성 등)는 `docs/automation/AUTOMATION_GUIDE.md`를 따릅니다.

## 5. Document Management 원칙

- PRD, TC, Roadmap 등 산출물은 `/docs` 하위에 Markdown으로 관리합니다.
- 문서가 변경될 때는 변경 날짜와 변경 사유를 문서 내 이력에 기록합니다.
- 문서 파일명·구조 규칙은 실제 문서를 처음 생성하는 시점에 확정합니다.

## 6. Sub Agent / Skill 역할 분리 원칙

- 각 Sub Agent/Skill은 단일 책임만 가지며(PRD 작성 / TC 생성 / Roadmap 작성 /
  자동화 구현 / 테스트 실행 / 리포트 생성 / Slack 알림 등), 역할이 서로 중복되지 않습니다.
- 한 Agent가 다른 Agent의 책임 범위를 임의로 침범하지 않습니다.
- 새로운 역할이 필요하면 기존 Agent를 확장하기보다 책임이 분리된 새 Agent/Skill 생성을 우선 검토합니다.

## 7. Approved Artifact Protection 원칙

- 사용자가 승인한 상위 단계 산출물(PRD, TC, Roadmap 등)을 후속 Agent가 임의로 수정하지 않습니다.
  - 승인된 PRD를 TC 작성 Agent가 임의 수정하지 않습니다.
  - 승인된 TC를 Roadmap/자동화 구현 Agent가 임의 수정하지 않습니다.
  - 승인된 Roadmap을 구현 과정에서 임의로 변경하지 않습니다.
- 구현 중 상위 산출물의 변경이 필요하다고 판단되면, 변경이 필요한 이유와 영향을 사용자에게 보고하고
  재승인을 받은 후에만 반영합니다.

## 8. Source of Truth 원칙

산출물 간 내용이 겹치거나 다른 시점에 갱신될 수 있으므로, 각 판단 기준의 우선순위(Source of Truth)를 아래와 같이 고정합니다.

| 판단 기준 | Source of Truth |
|---|---|
| 요구사항 기준 | 승인된 PRD |
| Risk 우선순위 기준 | 사용자가 작성한 Feature Risk Matrix (Google Sheet, AI 비관여, 리스크 점수는 사용자 확정 전까지 비어 있을 수 있음) |
| QA 전략/범위 기준 | 사용자가 작성한 Project QA Strategy (Google Sheet, AI 비관여) |
| Test Scenario 기준 | 승인된 TC |
| 자동화 구현 범위 | 승인된 TC + 승인된 Roadmap |
| Regression 범위 | 사용자가 입력한 "Regression 여부" = O (Google Sheet, AI 비관여) |
| 정기 실행 대상 | 사용자가 최종 선정한 자동화 대상 TC (승인된 TC + 선정 결과) |
| 실제 구현 상태 | Repository Code |
| CI 실행 결과 | GitHub Actions Result |

Google Sheet로만 관리되는 Feature Risk Matrix/Project QA Strategy는 AI가 생성·수정하지
않으며, 읽기 전용 참고자료로만 사용합니다.

- PRD, TC, Roadmap, Code 등 산출물 간 내용이 서로 충돌하는 경우, 후속 Agent가 임의로
  하나를 선택하거나 상위 산출물을 수정하지 않습니다.
- 충돌이 발견되면 충돌 내용을 사용자에게 보고하고, 확인 또는 승인을 받은 후에만 다음 작업을 진행합니다.

## 9. Agent Hand-off 원칙

- Agent는 **승인된** 이전 단계 산출물만 입력으로 사용합니다.
- Agent 간 산출물은 [4. Directory Structure]에 정의된 저장 위치를 통해 전달합니다.
- 이전 단계 산출물이 아직 승인되지 않은 상태라면 후속 Agent는 해당 산출물을 기반으로 작업을 진행하지 않습니다.
- 산출물의 구체적인 포맷(JSON Schema, Markdown Template 등)은 이 문서에서 정의하지 않으며,
  해당 산출물을 다루는 Agent/Skill에서 정의합니다.

## 10. Test Automation 기본 원칙

- 자동화 테스트는 독립적으로 실행 가능하고(Isolated), 재현 가능하며(Reproducible), 반복 실행해도
  같은 결과를 내야 합니다(Idempotent).
- 프레임워크별 세부 컨벤션(API 사용법, 셀렉터 전략 등)과 Page Object, Locator, Utils, Config 등
  자동화 코드의 상세 Architecture는 이 문서에서 정의하지 않고
  `docs/automation/AUTOMATION_GUIDE.md`에서 정의합니다.

## 11. Test Data 관리 원칙

- Production 데이터의 생성/수정/삭제는 **사용자의 명시적인 승인 없이 수행하지 않습니다.**
- Production 환경 또는 Production 데이터를 기반으로 검증해야 하는 경우에도, 목적과 영향(발생 가능한
  부작용 포함)을 사용자에게 설명하고 승인을 받은 후에만 진행합니다.
- 테스트 간 데이터 오염과 의존성을 최소화합니다(각 테스트는 자신의 데이터를 스스로 준비/정리).
- 민감정보(개인정보, 인증정보 등)를 테스트 데이터에 포함하지 않습니다.

## 12. Code Change 기본 원칙

- 동일하거나 유사한 기능을 불필요하게 중복 구현하지 않습니다.
- 요구사항과 무관한 코드를 임의로 수정하지 않습니다.
- 불필요한 파일이나 코드를 생성하지 않습니다.
- 기존 프로젝트 구조와 Naming Convention을 우선 준수합니다.
- 구현 방향에 큰 영향을 주는 요구사항이 불명확하면 임의로 결정하지 않고 사용자에게 확인합니다.

## 13. Test 실행 및 검증 원칙

- 코드 작성 후 가능한 범위에서 관련 테스트를 실행합니다.
- 신규 자동화 코드를 작성하거나 기존 코드를 변경한 경우, 해당 변경에 영향을 받는 테스트 범위를 확인합니다.
- 테스트 실패가 발생하면 가능한 범위에서 원인을 다음 중 하나로 구분합니다.
  - Automation Code 문제
  - Test Data 문제
  - Test Environment 문제
  - 실제 Product 문제
- 테스트 실패를 임의로 PASS로 판단하지 않습니다.
- 실패를 회피하기 위해 무한/반복적으로 재시도하지 않습니다.
- 실패 원인이 명확하지 않은 경우, 추측으로 결론 내리지 않고 사용자에게 상황을 보고합니다.

## 14. Git / GitHub 사용 원칙

- Claude는 사용자의 승인 없이 임의로 Git Commit을 수행하지 않습니다.
- 코드 작성 완료와 Git Commit을 동일한 작업으로 취급하지 않습니다.
- 코드 구현이 완료되면 Commit 전에 반드시 변경 결과와 예정 Commit Message를 사용자에게 보고하고 승인을 받습니다.
- Git Push 역시 사용자의 별도 승인 없이 수행하지 않습니다.

## 15. CI 운영 원칙

GitHub Actions를 CI 실행 환경으로 사용하며, 다음 운영 흐름을 기준으로 삼습니다.

```
트리거(Push / 정기 실행(Cron) / 수동 실행) → GitHub Actions → 자동화 테스트 실행 → Test Report 생성 → 결과 판정 → Slack Notification
```

정기 실행은 사용자가 최종 선정한 핵심 Regression TC로 공개 서비스의 주요 기능 이상을 감지하는
것을 목표로 합니다. Push는 자동화 코드 변경 검증 용도입니다. 트리거별 실행 범위는 새 TC 설계와
자동화 대상 선정이 끝난 뒤 결정합니다.

- 자동화 대상 선정과 CI 설정이 확정되기 전에는 정기 실행을 활성화하지 않습니다.
- 정기 실행이 실패하면 결과 수집과 리포트 생성은 자동으로 수행합니다.

CI에서는 다음 작업을 수행할 수 있도록 고려합니다.

- 자동화 테스트 실행
- Test Result 수집
- Test Report 생성
- 실패 테스트 확인
- 실패 원인 분류 및 분석([13. Test 실행 및 검증 원칙] 기준)
- Artifact 저장
- Slack 성공/실패 알림

이 문서는 CI **운영 원칙**만 정의합니다. 현재 GitHub Actions Workflow(YAML)는 이전 구성이며,
새 실행 범위가 확정되면 수정합니다.

## 16. Slack Notification 원칙

- Slack은 CI 자동화 테스트 결과 알림 용도로만 사용합니다.
- Slack을 Commit 또는 Push 승인 용도로 사용하지 않습니다. 승인은 항상 사용자와의
  직접적인 확인을 통해 이루어집니다.

## 17. Security / Secret 관리 원칙

- GitHub Token, Slack Webhook URL 등 민감정보를 코드에 하드코딩하지 않습니다.
- 로컬 환경에서는 `.env` 등으로 분리하고 `.gitignore`에 포함합니다.
- CI 환경에서는 GitHub Secrets를 사용합니다.
- 커밋 전 변경 파일에 민감정보가 포함되어 있지 않은지 확인합니다.

## 18. User Approval 원칙

다음 작업은 워크플로우상의 단계 번호와 무관하게 **항상** 사용자 승인이 필요한 작업으로 정의합니다.

- Project PRD 승인
- Feature PRD 승인
- Regression 범위 지정 ("Regression 여부" O/X 입력, AI는 이 열에 값을 입력하지 않음)
- TC 자동화 대상 최종 선정
- 정기 실행 대상 TC의 신규 추가 또는 제외
- 정기 실행 주기 및 실행 환경의 변경
- Git Commit
- Git Push

AI는 PRD 초안과 자동화 후보를 추천할 수 있지만, PRD 확정, 최종 자동화 대상, Commit/Push 여부는 항상 사용자가 결정합니다.
자동화 대상 선정은 사용자의 요청이 있을 때만 수행하며, AI는 추천까지만 합니다.

### 정기 실행 승인 범위

- GitHub Actions에서 이미 승인된 자동화 TC를 정기 실행하는 것은 추가 사용자 승인 없이 수행합니다.
- 정기 실행 대상 TC를 신규 추가하거나 제외하는 경우 사용자 승인을 받습니다.
- 정기 실행 주기 및 실행 환경을 변경하는 경우 사용자 승인을 받습니다.
- 자동화 대상 선정 및 CI 설정이 확정되기 전에는 정기 실행을 활성화하지 않습니다.
- 정기 실행 실패 시 결과 수집 및 리포트 생성은 자동으로 수행합니다.
- 이 규칙은 변경 작업에 대한 승인 기준입니다. 실제 GitHub Actions 실행 시점에 사용자 승인을
  요구하는 구조(수동 승인 게이트 등)로 구현하지 않습니다.

## 19. Scope Control 원칙

프로젝트가 어느 단계에 있든 아래 원칙을 공통으로 적용합니다. 특정 단계를 기준으로
금지 목록을 나열하지 않고, 아래 원칙으로 범위를 통제합니다.

- 현재 사용자가 명시적으로 요청했거나 승인한 작업 범위만 수행합니다.
- 현재 진행 중인 작업의 다음 단계에 해당하는 산출물을 임의로 선행 생성하지 않습니다.
  - 예: PRD Agent/Skill을 구성하는 중에는 PRD 문서를 임의로 생성하지 않습니다.
  - 예: PRD를 작성하는 중에는 TC를 임의로 생성하지 않습니다.
  - 예: TC를 작성하는 중에는 Roadmap이나 자동화 코드를 임의로 생성하지 않습니다.
  - 예: 자동화 코드를 구현하는 중에는 사용자 승인 없이 Git Commit/Push를 수행하지 않습니다.
- 다음 단계 작업이 필요하다고 판단되면 임의로 수행하지 않고, 사용자에게 제안한 뒤
  승인을 받은 후에만 진행합니다.
- 이 원칙은 [7. Approved Artifact Protection], [8. Source of Truth], [9. Agent Hand-off],
  [18. User Approval] 원칙과 함께 적용되며, 프로젝트의 특정 단계에 고정되지 않고
  전체 기간 동안 동일하게 유지됩니다.
