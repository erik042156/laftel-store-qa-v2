---
문서유형: Test Case
상태: 초안   # 초안 | 승인완료
관련 Feature PRD: prd/Feature/prd-product-detail.md
최초 작성일: 2026-10-21
최근 변경일: 2026-10-22
승인일:
---

# Test Case - 상품상세 (번호 표기 규칙 반영본)

> 이 문서는 `docs/tc/revised6/product-detail.md`(62건)의 `Test Scenario` 컬럼을 `3 Depth`(테스트 시나리오/목적) 컬럼으로 바꾼 새 문서(revised7)다. 3 Depth는 기존 시나리오 문장을 `{검증 대상} {목적 분류}` 형태의 짧은 목적 문구로 다시 쓴 것이며, 이외 컬럼 값(ID, 1·2 Depth, Preconditions, Steps, Expected, Priority, Requirement ID, Result)과 행 순서는 revised6와 동일하다. 대표 TC 참조(괄호)는 3 Depth에 유지했다. 기존 문서·Spreadsheet는 변경하지 않았다.
> 이 문서는 `docs/tc/revised5/product-detail.md`(62건)를 새 TC 컬럼 구조(`ID | 1 Depth | 2 Depth | Test Scenario | Preconditions | Test Steps | Expected Result | Priority | Requirement ID | Result`)로 변환한 새 문서(revised6)다. `Feature` 컬럼을 `1 Depth`(시스템/도메인)와 `2 Depth`(세부 기능/컴포넌트)로 나누고 `Requirement ID`를 Priority 뒤로 옮겼으며, ID·Scenario·Preconditions·Steps·Expected·Priority·Requirement ID·Result 값과 행 순서는 revised5와 동일하다. 기존 문서·Spreadsheet는 변경하지 않았다.
> 이 문서는 `docs/tc/revised4/product-detail.md`(62건)를 개정된 tc-writing Skill의 **1.5 표기 규칙(복수 항목은 `1.`, `2.` 번호 + `<br>` 구분)** 으로 재작성한 **새 문서**이다. 표기 형식만 변경했으며 TC의 ID·Requirement ID·Test Scenario·Priority·내용의 의미·행 구성(62건)·ID 오름차순 정렬은 revised4와 동일하다. 기존 문서(`docs/tc/product-detail.md`, `revised/`~`revised4/`)와 Spreadsheet는 변경하지 않았으며, Spreadsheet에도 반영하지 않았다.
> 공통 전제: PC Chrome, Production(https://store.laftel.net/). "로그인"은 테스트 계정 로그인 상태, "비로그인"은 로그아웃(시크릿 창) 상태를 의미하며 계정 정보는 문서에 기록하지 않는다. 별도 명시가 없으면 로그인 여부와 무관하며, **판매중 상품의 상품상세 화면(`/products/{상품번호}`)에 진입한 상태**를 기본 전제로 한다. 각 TC의 Preconditions에는 이 기본 전제에 추가로 필요한 조건만 적는다. PRD에 상품 번호가 정의되어 있지 않아 특정 상품 상태(판매중/예약구매/판매종료/품절), 옵션 유무 등은 "사전에 확인해 둔 상품"을 사용한다.
> 작성 형식: Test Steps에는 사용자 동작 1개(1~2단계)만 쓰고 이전 진입·상태는 Preconditions에 쓴다. Test Steps·Preconditions·Expected Result는 명사형 간략 표기로 쓰며, 항목이 2개 이상일 때만 `1.`, `2.` 번호를 항목마다 붙이고 항목 사이는 `<br>`로 구분한다(단일 항목은 번호 없음). Preconditions는 독립된 조건 단위로 나누어 번호를 붙인다.
> Production 데이터 변경 표기: 찜 추가/해제(TC-PRODUCT-DETAIL-028, 030, 061~064)와 최근 본 상품 기록(TC-PRODUCT-DETAIL-041)은 테스트 계정의 Production 데이터를 생성/변경한다. 해당 TC의 Preconditions에 "[Production 데이터 변경]"으로 표기했으며 실행 전 사용자 승인이 필요하다(CLAUDE.md 11절). 찜은 TC 수행 후 원상태(해제)로 복구한다.
> Risk 참조: Risk 스프레드시트 `리스크 매트릭스`(RI-PRODUCT-DETAIL-001~012, 확정값)를 읽기 전용으로 참조했다(revised2와 동일한 매핑). High(RI-009, 010, 011)는 정상·예외·상태 전이·경계·정합성을 동작별로 다층 구성하고, Medium은 대표 동작별, Low는 기본 표시 확인으로 구성했다.
> Feature 간 연계: 찜 추가/해제·로그인 유도 팝업 공통 동작은 `docs/tc/wishlist.md`(원본)·`docs/tc/revised/wishlist.md`가 다루며, 이 문서의 찜 TC는 상품상세 하단 찜 아이콘·같은 작품 굿즈 카드 찜 아이콘 진입점과 찜 목록 반영 연계만 검증한다(겹침 후보는 아래 "미결 질문" 참조, 이번에도 정리하지 않고 동작 기준으로 유지). 검색 결과에서 판매종료/품절 상품으로 진입하는 TC-SEARCH-013, 014는 진입 경로 검증이며, 하단 버튼 상태의 대표 TC는 TC-PRODUCT-DETAIL-038, 039이다.
> 제외 범위(기존과 동일): 상품상세 URL 직접 진입(이전 화면 없음) 후 뒤로가기의 기대 이동 위치는 PRD에 명시되어 있지 않아 TC로 만들지 않았다. 안내 박스 문구 일치 여부는 상품별로 상이하므로 판정하지 않는다.

## TC 목록

| ID | 1 Depth | 2 Depth | 3 Depth | Preconditions | Test Steps | Expected Result | Priority | Requirement ID | Result |
|---|---|---|---|---|---|---|---|---|---|
| TC-PRODUCT-DETAIL-001 | 상품상세 | 상품상세 진입 | 메인 배너 클릭 상품상세 진입 성공 케이스 | 1. 메인페이지(`/`) 진입<br>2. 상품상세로 랜딩되는 최상단 배너 존재 | 최상단 배너 클릭 | 1. 상품상세 화면 표시<br>2. URL: `/products/{상품번호}` | P1 | REQ-PRODUCT-DETAIL-001 |  |
| TC-PRODUCT-DETAIL-002 | 상품상세 | 상품상세 진입 | 찜한 상품 섹션 클릭 상품상세 진입 성공 케이스 | 1. 로그인<br>2. 내 스토어(`/my`) 진입<br>3. "찜한 상품" 섹션에 상품 1건 이상 노출 | "찜한 상품" 섹션 내 상품 클릭 | 1. 클릭한 상품의 상품상세 화면 표시<br>2. URL: `/products/{상품번호}` | P1 | REQ-PRODUCT-DETAIL-003 |  |
| TC-PRODUCT-DETAIL-003 | 상품상세 | 상품상세 진입 | 장바구니 상품 클릭 상품상세 진입 성공 케이스 | 1. 로그인<br>2. 장바구니 페이지에 담긴 상품 1건 이상 존재(기존 데이터 사용, 신규 생성 안 함) | 장바구니 페이지 내 담긴 상품 클릭 | 1. 클릭한 상품의 상품상세 화면 표시<br>2. URL: `/products/{상품번호}` | P1 | REQ-PRODUCT-DETAIL-005 |  |
| TC-PRODUCT-DETAIL-005 | 상품상세 | 상품상세 진입 | URL 직접 입력 상품상세 진입 성공 케이스 | 존재하는 상품 번호 사전 확인 | 주소창에 `https://store.laftel.net/products/{상품번호}` 입력 후 이동 | 1. 해당 상품의 상품상세 화면 표시<br>2. 상품명, 가격, 하단 찜/구매 영역 노출 | P1 | REQ-PRODUCT-DETAIL-006 |  |
| TC-PRODUCT-DETAIL-006 | 상품상세 | 상품상세 진입 | 존재하지 않는 상품 번호 접근 404 페이지 네거티브 검증 | 없음 | 주소창에 `https://store.laftel.net/products/2` 입력 후 이동 | 1. 커스텀 404 페이지 표시<br>2. "이런, 이미 사라진 페이지군요." 안내 및 "삭제된 페이지거나 잘못된 주소입니다. 라프텔 홈으로 이동해 주세요. 아니면, 함께 범인을 찾아볼까요?" 문구 노출<br>3. "홈으로 이동" 버튼, "범인 찾아보기" 링크 노출 | P1 | REQ-PRODUCT-DETAIL-007 |  |
| TC-PRODUCT-DETAIL-007 | 상품상세 | 상단 바 | 상단 바 아이콘 구성 표시 검증 | 1. 로그인<br>2. 장바구니에 상품 1건 이상 담김 | 화면 상단 바 확인 | 1. 상단 바 내 뒤로가기("<") 표시<br>2. 검색 아이콘 표시<br>3. 장바구니 아이콘 및 담긴 수량 뱃지 표시 | P1 | REQ-PRODUCT-DETAIL-009 |  |
| TC-PRODUCT-DETAIL-008 | 상품상세 | 상단 바 | 상단 바 검색 아이콘 클릭 검색페이지 이동 검증 | 없음 | 상단 바 내 검색 아이콘 클릭 | 1. 검색페이지 표시<br>2. URL: `/search` | P1 | REQ-PRODUCT-DETAIL-010 |  |
| TC-PRODUCT-DETAIL-009 | 상품상세 | 상단 바 | 메인 진입 상품상세 뒤로가기 복귀 검증 | 메인페이지(`/`) 상품 리스트의 상품 클릭으로 상품상세에 진입한 상태 | 상단 바 내 뒤로가기("<") 클릭 | 메인페이지(`/`) 표시 | P1 | REQ-PRODUCT-DETAIL-012 |  |
| TC-PRODUCT-DETAIL-010 | 상품상세 | 이미지 캐러셀 | 이미지 캐러셀 다음 사진 전환 성공 케이스 | 1. 이미지 2장 이상인 상품<br>2. 첫 번째 사진("1/M") 표시 상태 | 이미지 우→좌 스와이프 | 1. 다음 사진 표시<br>2. 페이지네이션 "1/M" → "2/M" 갱신 | P1 | REQ-PRODUCT-DETAIL-013, REQ-PRODUCT-DETAIL-015 |  |
| TC-PRODUCT-DETAIL-011 | 상품상세 | 이미지 캐러셀 | 이미지 캐러셀 첫 사진 이전 이동 순환 경계값 검증 | 1. 이미지 2장 이상인 상품<br>2. 첫 번째 사진 표시 상태 | 이미지 좌→우 스와이프 | 1. 마지막 사진 표시<br>2. 페이지네이션 "M/M" | P1 | REQ-PRODUCT-DETAIL-014 |  |
| TC-PRODUCT-DETAIL-012 | 상품상세 | 작품명 | 작품명 클릭 작품 페이지 이동 검증 | 작품명(예: "원피스 >")이 표시되는 상품 | 작품명 클릭 | 1. 새 탭 미오픈<br>2. 같은 탭에서 해당 작품 페이지 표시 | P1 | REQ-PRODUCT-DETAIL-016 |  |
| TC-PRODUCT-DETAIL-013 | 상품상세 | 상품 기본 정보 | 상품명·가격 표시 검증 | 없음 | 이미지 캐러셀 아래 영역 확인 | 1. 상품명 표시<br>2. 가격 표시 | P1 | REQ-PRODUCT-DETAIL-017 |  |
| TC-PRODUCT-DETAIL-015 | 상품상세 | 상품 기본 정보 | 발송예정 안내 아이콘 클릭 팝업 표시 검증 | 없음 | 발송예정 안내 아이콘(ⓘ) 클릭 | 1. "발송예정 안내" 팝업 표시<br>2. 배송 일정은 영업일 기준이라는 안내 포함<br>3. 판매사/택배사/상품 준비 상황에 따라 발송 예정일이 달라질 수 있다는 안내 포함<br>4. "확인" 버튼 포함 | P1 | REQ-PRODUCT-DETAIL-019 |  |
| TC-PRODUCT-DETAIL-016 | 상품상세 | 같은 작품 굿즈 | 같은 작품 굿즈 캐러셀 카드 구성 표시 검증 | 같은 작품 굿즈가 존재하는 상품 | "같은 작품 굿즈" 영역으로 스크롤 | 1. 개별 상품 카드 캐러셀 나열<br>2. 카드별 이미지, 찜 아이콘, 가격 표시<br>3. 해당 카드에 "예약구매"/"NEW" 등 뱃지 표시 | P1 | REQ-PRODUCT-DETAIL-020 |  |
| TC-PRODUCT-DETAIL-017 | 상품상세 | 같은 작품 굿즈 | 같은 작품 굿즈 카드 클릭 상품상세 이동 검증 | 같은 작품 굿즈가 존재하는 상품 | 캐러셀 카드 내 이미지 영역(찜 아이콘 제외) 클릭 | 1. 클릭한 카드 상품의 상품상세 페이지 표시<br>2. URL: `/products/{해당 상품번호}` | P1 | REQ-PRODUCT-DETAIL-021 |  |
| TC-PRODUCT-DETAIL-018 | 상품상세 | 같은 작품 굿즈 | 같은 작품 굿즈 더보기 클릭 목록 이동 검증 | 같은 작품 굿즈가 존재하는 상품 | "같은 작품 굿즈" 영역 내 "더보기" 클릭 | 1. URL: `/products/{id}/related`<br>2. 상단 "같은 작품 굿즈" 타이틀, 뒤로가기, 장바구니 아이콘 표시<br>3. 상품 2열 그리드 나열 | P1 | REQ-PRODUCT-DETAIL-022 |  |
| TC-PRODUCT-DETAIL-019 | 상품상세 | 상세정보/아코디언 | 상세정보 탭 안내 박스·상세 이미지 표시 검증 | 없음 | "상세정보" 탭 영역으로 스크롤 | 1. 안내 박스 노출<br>2. 상품 상세 이미지 배너 노출<br>3. (안내 박스 항목/문구는 상품별로 상이하므로 문구 일치 여부 판정 제외) | P1 | REQ-PRODUCT-DETAIL-023, REQ-PRODUCT-DETAIL-024 |  |
| TC-PRODUCT-DETAIL-020 | 상품상세 | 상세정보/아코디언 | 상세정보 더보기 토글 펼침 검증 | "상세정보 더보기" 토글이 있는 상품 | "상세정보 더보기" 토글 클릭 | 하단 숨김 상세 이미지/설명 펼침 표시 | P1 | REQ-PRODUCT-DETAIL-025 |  |
| TC-PRODUCT-DETAIL-021 | 상품상세 | 상세정보/아코디언 | 상세정보 아코디언 3개 항목 표시 검증 | 없음 | 상세정보 탭 하단 아코디언 영역으로 스크롤 | "상품정보 제공고시", "판매자 정보", "유의사항" 3개 항목 표시 | P1 | REQ-PRODUCT-DETAIL-026 |  |
| TC-PRODUCT-DETAIL-022 | 상품상세 | 상세정보/아코디언 | 상품정보 제공고시 페이지 표 표시 검증 | 아코디언 "상품정보 제공고시" 클릭으로 `/products/{id}/product-info` 진입 상태 | 페이지 내용 확인 | 브랜드, 원산지, 출시일, 제조사, 공급사, 자체분류 표 형태 표시 | P1 | REQ-PRODUCT-DETAIL-027 |  |
| TC-PRODUCT-DETAIL-025 | 상품상세 | 상세정보/아코디언 | 페이지 최하단 공통 푸터 표시 검증 | 없음 | 페이지 최하단까지 스크롤 | 1. 아코디언 하단 공통 푸터 노출<br>2. 푸터 내 사업자 정보 포함<br>3. 푸터 내 회사소개/고객센터/공지사항/이용약관/청소년보호정책/개인정보처리방침/저작권 표기 포함<br>4. 푸터 내 SNS 링크 포함 | P2 | REQ-PRODUCT-DETAIL-031 |  |
| TC-PRODUCT-DETAIL-026 | 상품상세 | 하단 고정 영역 | 스크롤 시 하단 찜/구매 영역 고정 표시 검증 | 상품상세 최상단에서 하단 찜(하트) 아이콘과 상태별 버튼 표시 | 1. 페이지 중간까지 스크롤<br>2. 최하단(푸터)까지 스크롤 | 1. 중간 스크롤 위치에서 하단 찜(하트) 아이콘, 상태별 버튼 고정 표시<br>2. 최하단 스크롤 위치에서 하단 찜(하트) 아이콘, 상태별 버튼 고정 표시 | P0 | REQ-PRODUCT-DETAIL-032 |  |
| TC-PRODUCT-DETAIL-027 | 상품상세 | 하단 찜 아이콘 | 비로그인 하단 찜 아이콘 클릭 로그인 유도 팝업 네거티브 검증 | 1. 비로그인<br>2. 찜 동작 대표 TC: TC-WISHLIST-004 | 하단 찜 아이콘 클릭 | 1. "로그인 후 이용해 주세요." 팝업 표시(취소/로그인 버튼 포함)<br>2. 하트 아이콘 빈 하트 유지<br>3. "찜한 상품에 추가했어요" 토스트 미표시 | P0 | REQ-PRODUCT-DETAIL-033 |  |
| TC-PRODUCT-DETAIL-028 | 상품상세 | 하단 찜 아이콘 | 로그인 하단 찜 아이콘 클릭 찜 추가 성공 케이스 | 1. 로그인<br>2. 찜하지 않은 상품<br>3. **[Production 데이터 변경]** 테스트 계정의 찜 목록, 사용자 승인 후 수행, TC-PRODUCT-DETAIL-062 등으로 해제해 원상태 복구<br>4. 찜 동작 대표 TC: TC-WISHLIST-002 | 하단 찜 아이콘 클릭 | 1. "찜한 상품에 추가했어요" 토스트 노출<br>2. 하트 아이콘 빈 하트 → 채워진 보라색 하트 변경 | P0 | REQ-PRODUCT-DETAIL-034 |  |
| TC-PRODUCT-DETAIL-030 | 상품상세 | 같은 작품 굿즈 | 같은 작품 굿즈 카드 찜 아이콘 클릭 찜 처리 검증 | 1. 로그인<br>2. 찜하지 않은 "같은 작품 굿즈" 카드가 있는 상품<br>3. **[Production 데이터 변경]** 테스트 계정의 찜 목록, 사용자 승인 후 수행, 수행 후 찜 해제로 복구 | 캐러셀 카드 내 찜 아이콘 클릭 | 1. 해당 카드 상품의 상세 페이지 미이동, 현재 화면 유지<br>2. "찜한 상품에 추가했어요" 토스트 노출<br>3. 해당 카드 하트 아이콘 보라색 변경 | P1 | REQ-PRODUCT-DETAIL-049 |  |
| TC-PRODUCT-DETAIL-031 | 상품상세 | 구매하기/옵션 선택 | 옵션 없는 상품 구매하기 클릭 수량선택 UI 표시 검증 | 옵션이 없는 판매중 상품 | 하단 "구매하기" 버튼 클릭 | 1. 페이지 이동 없이 같은 화면 하단 구매 영역 확장 노출<br>2. 옵션 선택 단계 없이 수량선택 UI 노출(수량 1)<br>3. 총 금액 노출<br>4. 장바구니/바로구매 버튼 노출 | P0 | REQ-PRODUCT-DETAIL-035, REQ-PRODUCT-DETAIL-038, REQ-PRODUCT-DETAIL-039 |  |
| TC-PRODUCT-DETAIL-032 | 상품상세 | 구매하기/옵션 선택 | 옵션 상품 구매하기 클릭 옵션 드롭다운·품절 옵션 표시 검증 | 옵션이 있고 품절 옵션과 선택 가능한 옵션이 모두 포함된 판매중 상품 | 하단 "구매하기" 버튼 클릭 | 1. 별도 페이지 이동 없이 옵션 선택 드롭다운 먼저 펼침<br>2. 품절 옵션 회색 처리 및 "품절" 라벨 표시<br>3. 선택 가능한 옵션 정상 노출 | P0 | REQ-PRODUCT-DETAIL-035, REQ-PRODUCT-DETAIL-036 |  |
| TC-PRODUCT-DETAIL-033 | 상품상세 | 구매하기/옵션 선택 | 품절 옵션 클릭 선택 불가 네거티브 검증 | 1. 옵션이 있고 품절 옵션이 포함된 판매중 상품<br>2. "구매하기" 클릭으로 옵션 드롭다운 펼침 상태 | "품절" 라벨 옵션 클릭 | 1. 해당 옵션 미선택<br>2. 선택 옵션명, 수량선택 UI 미표시<br>3. 총 금액 변경 없음 | P0 | REQ-PRODUCT-DETAIL-036 |  |
| TC-PRODUCT-DETAIL-034 | 상품상세 | 구매하기/옵션 선택 | 옵션 선택 시 옵션명·수량 UI·총 금액 갱신 성공 케이스 | 1. 옵션 가격이 서로 다른 옵션 2개 이상이 선택 가능한 판매중 상품<br>2. "구매하기" 클릭으로 옵션 드롭다운 펼침 상태 | 선택 가능한 옵션 A 클릭 | 1. 드롭다운 닫힘<br>2. 선택 옵션명, 수량선택 UI, 옵션별 가격 표시<br>3. "총 금액" 옵션 A 가격 기준 표시 | P0 | REQ-PRODUCT-DETAIL-037 |  |
| TC-PRODUCT-DETAIL-035 | 상품상세 | 구매하기/옵션 선택 | 최소 수량(1) 감소 조작 경계값 검증 | 1. 옵션이 없는 판매중 상품<br>2. "구매하기" 클릭으로 수량선택 UI 노출<br>3. 수량 1 상태 | 수량 감소 조작 | 수량 1 유지(1 미만 감소 불가) | P0 | REQ-PRODUCT-DETAIL-039 |  |
| TC-PRODUCT-DETAIL-036 | 상품상세 | 판매 상태별 버튼 | 판매중 상품 구매하기 버튼 활성 표시 검증 | 판매중 상품 | 하단 버튼 확인 | 1. 버튼 텍스트 "구매하기"<br>2. 버튼 활성화(보라색) | P0 | REQ-PRODUCT-DETAIL-040, REQ-PRODUCT-DETAIL-041 |  |
| TC-PRODUCT-DETAIL-037 | 상품상세 | 판매 상태별 버튼 | 예약구매 상품 카운트다운·예약구매 버튼 표시 검증 | 예약구매 상태이며 예약 마감 전인 상품 | 이미지 영역, 하단 버튼 영역 확인 | 1. 이미지 영역 "예약 마감까지 D일 HH:MM" 형식 카운트다운 표시<br>2. 하단 버튼 "예약 마감까지 D일 HH:MM" 형식 카운트다운 표시<br>3. 버튼 텍스트 "예약구매"(활성, 보라색) | P0 | REQ-PRODUCT-DETAIL-040, REQ-PRODUCT-DETAIL-042 |  |
| TC-PRODUCT-DETAIL-038 | 상품상세 | 판매 상태별 버튼 | 품절 상품 품절 버튼 비활성·찜 아이콘 활성 표시 검증 | 품절 상품 | 하단 버튼, 찜 아이콘 상태 확인 | 1. 하단 버튼 "품절" 텍스트, 비활성화(회색조)<br>2. 찜 아이콘 활성 상태 | P0 | REQ-PRODUCT-DETAIL-040, REQ-PRODUCT-DETAIL-043 |  |
| TC-PRODUCT-DETAIL-039 | 상품상세 | 판매 상태별 버튼 | 판매종료 상품 판매종료 버튼 비활성·찜 아이콘 활성 표시 검증 | 판매종료 상품 | 하단 버튼, 찜 아이콘 상태 확인 | 1. 하단 버튼 "판매종료" 텍스트, 비활성화(회색조)<br>2. 찜 아이콘 활성 상태 | P0 | REQ-PRODUCT-DETAIL-040, REQ-PRODUCT-DETAIL-044 |  |
| TC-PRODUCT-DETAIL-040 | 상품상세 | 판매 상태별 버튼 | 품절 버튼 클릭 무반응 네거티브 검증 | 품절 상품 | 하단 "품절" 버튼 클릭 | 1. 구매 영역 확장, 옵션/수량 UI 노출, 팝업, 페이지 이동 없음<br>2. 화면 상태 클릭 전과 동일 | P0 | REQ-PRODUCT-DETAIL-045 |  |
| TC-PRODUCT-DETAIL-041 | 상품상세 | 최근 본 상품 기록 | 상품상세 진입 후 최근 본 상품 자동 기록 검증 | 1. 로그인<br>2. 최근 본 상품 목록에 없는 상품의 상품상세 진입 상태<br>3. **[Production 데이터 변경]** 테스트 계정의 최근 본 상품 기록, 사용자 승인 후 수행 | 내 스토어 > 최근 본 상품 확인 | 방금 진입한 상품 최근 본 상품 목록 기록 표시 | P1 | REQ-PRODUCT-DETAIL-046 |  |
| TC-PRODUCT-DETAIL-042 | 상품상세 | 로그인 상태별 화면 구성 | 로그인/비로그인 화면 구성 동일 검증 | 동일 상품(판매중)을 로그인 창과 비로그인 창(시크릿 창)에서 각각 진입 가능 | 1. 로그인 상태에서 화면 구성(상단 바, 캐러셀, 상품 정보, 배송정보, 같은 작품 굿즈, 상세정보, 아코디언, 푸터, 하단 영역) 확인<br>2. 비로그인 상태에서 같은 상품의 동일 영역 확인 | 1. 두 상태 간 화면 구성 요소, 노출 순서 동일<br>2. (찜 클릭 시 동작 차이, 장바구니 수량 뱃지 등 계정 종속 데이터는 비교 제외) | P1 | REQ-PRODUCT-DETAIL-047 |  |
| TC-PRODUCT-DETAIL-043 | 상품상세 | 상품상세 진입 | 메인 상품 리스트 클릭 상품상세 진입 성공 케이스 | 1. 메인페이지(`/`) 진입<br>2. 상품 리스트에 상품 1건 이상 노출 | 상품 리스트 내 임의 상품 클릭 | 1. 클릭한 상품의 상품상세 화면 표시<br>2. URL: `/products/{상품번호}` | P1 | REQ-PRODUCT-DETAIL-002 |  |
| TC-PRODUCT-DETAIL-044 | 상품상세 | 상품상세 진입 | 최근 본 상품 클릭 상품상세 진입 성공 케이스 | 1. 로그인<br>2. 내 스토어(`/my`) 진입<br>3. "최근 본 상품" 섹션에 상품 1건 이상 노출 | "최근 본 상품" 섹션 내 상품 클릭 | 1. 클릭한 상품의 상품상세 화면 표시<br>2. URL: `/products/{상품번호}` | P1 | REQ-PRODUCT-DETAIL-003 |  |
| TC-PRODUCT-DETAIL-045 | 상품상세 | 상품상세 진입 | 추천 상품 클릭 상품상세 진입 성공 케이스 | 1. 로그인<br>2. 내 스토어(`/my`) 진입<br>3. "추천 상품" 섹션에 상품 1건 이상 노출 | "추천 상품" 섹션 내 상품 클릭 | 1. 클릭한 상품의 상품상세 화면 표시<br>2. URL: `/products/{상품번호}` | P1 | REQ-PRODUCT-DETAIL-003 |  |
| TC-PRODUCT-DETAIL-046 | 상품상세 | 상품상세 진입 | 찜 상품 탭 클릭 상품상세 진입 성공 케이스 | 1. 로그인<br>2. 내 스토어 > 찜 "상품" 탭에 상품 1건 이상 노출 | "상품" 탭 내 상품 클릭 | 1. 클릭한 상품의 상품상세 화면 표시<br>2. URL: `/products/{상품번호}` | P1 | REQ-PRODUCT-DETAIL-004 |  |
| TC-PRODUCT-DETAIL-047 | 상품상세 | 상품상세 진입 | 찜 작품 탭 상품 클릭 상품상세 진입 성공 케이스 | 1. 로그인<br>2. 내 스토어 > 찜 "작품" 탭에 상품 1건 이상 노출 | "작품" 탭 내 상품 클릭 | 1. 클릭한 상품의 상품상세 화면 표시<br>2. URL: `/products/{상품번호}` | P1 | REQ-PRODUCT-DETAIL-004 |  |
| TC-PRODUCT-DETAIL-048 | 상품상세 | 상품상세 진입 | 주문내역 상품 클릭 상품상세 진입 성공 케이스 | 1. 로그인<br>2. 주문내역(`/orders`)에 주문 상품 1건 이상 존재(기존 데이터 사용, 신규 생성 안 함) | 주문내역 내 주문 상품 클릭 | 1. 클릭한 주문 상품의 상품상세 화면 표시<br>2. URL: `/products/{상품번호}` | P1 | REQ-PRODUCT-DETAIL-008 |  |
| TC-PRODUCT-DETAIL-049 | 상품상세 | 상단 바 | 상단 바 장바구니 아이콘 클릭 장바구니 이동 검증 | 없음 | 상단 바 내 장바구니 아이콘 클릭 | 1. 장바구니 페이지 표시<br>2. URL: `/cart?log_cart_entry_point=app_bar_cart_icon` | P1 | REQ-PRODUCT-DETAIL-011 |  |
| TC-PRODUCT-DETAIL-050 | 상품상세 | 상단 바 | 장바구니 진입 상품상세 뒤로가기 복귀 검증 | 1. 로그인<br>2. 장바구니 페이지의 상품 클릭으로 상품상세에 진입한 상태 | 상단 바 내 뒤로가기("<") 클릭 | 장바구니 페이지 표시 | P1 | REQ-PRODUCT-DETAIL-012 |  |
| TC-PRODUCT-DETAIL-051 | 상품상세 | 이미지 캐러셀 | 이미지 캐러셀 페이지네이션 "N/M" 표시 검증 | 이미지 2장 이상인 상품 | 이미지 캐러셀 내 페이지네이션 표기 확인 | 페이지네이션 "N/M" 형식 표시(예: "1/4") | P1 | REQ-PRODUCT-DETAIL-013 |  |
| TC-PRODUCT-DETAIL-052 | 상품상세 | 이미지 캐러셀 | 이미지 캐러셀 마지막 사진 다음 이동 순환 경계값 검증 | 1. 이미지 2장 이상인 상품<br>2. 마지막 사진 표시 상태 | 이미지 우→좌 스와이프 | 1. 첫 번째 사진 표시<br>2. 페이지네이션 "1/M" | P1 | REQ-PRODUCT-DETAIL-014 |  |
| TC-PRODUCT-DETAIL-053 | 상품상세 | 작품명 | 작품명·외부 이동 아이콘 표시 검증 | 작품명(예: "원피스 >")이 표시되는 상품 | 작품명 영역 확인 | 1. 작품명 표시<br>2. 외부 이동 아이콘 표시 | P1 | REQ-PRODUCT-DETAIL-016 |  |
| TC-PRODUCT-DETAIL-054 | 상품상세 | 상품 기본 정보 | 배송정보 섹션 구성 표시 검증 | 없음 | 배송정보 섹션 확인 | 1. 배송비 표시<br>2. 무료배송 기준 표시<br>3. 발송예정일 표시 | P1 | REQ-PRODUCT-DETAIL-018 |  |
| TC-PRODUCT-DETAIL-055 | 상품상세 | 상품 기본 정보 | 발송예정 안내 팝업 "확인" 화면 유지 검증 | 발송예정 안내 아이콘(ⓘ) 클릭으로 "발송예정 안내" 팝업 표시 상태 | 팝업 내 "확인" 버튼 클릭 | 1. 팝업 닫힘<br>2. 상품상세 화면 유지 | P1 | REQ-PRODUCT-DETAIL-019 |  |
| TC-PRODUCT-DETAIL-056 | 상품상세 | 상세정보/아코디언 | 아코디언 상품정보 제공고시 클릭 페이지 이동 검증 | 없음 | 아코디언 내 "상품정보 제공고시" 클릭 | 1. 별도 페이지 표시<br>2. URL: `/products/{id}/product-info` | P1 | REQ-PRODUCT-DETAIL-026 |  |
| TC-PRODUCT-DETAIL-057 | 상품상세 | 상세정보/아코디언 | 아코디언 판매자 정보 클릭 페이지 이동 검증 | 없음 | 아코디언 내 "판매자 정보" 클릭 | 1. 별도 페이지 표시<br>2. URL: `/products/{id}/seller-info` | P1 | REQ-PRODUCT-DETAIL-026 |  |
| TC-PRODUCT-DETAIL-058 | 상품상세 | 상세정보/아코디언 | 아코디언 유의사항 클릭 페이지 이동 검증 | 없음 | 아코디언 내 "유의사항" 클릭 | 1. 별도 페이지 표시<br>2. URL: `/products/{id}/notice` | P1 | REQ-PRODUCT-DETAIL-026 |  |
| TC-PRODUCT-DETAIL-059 | 상품상세 | 상세정보/아코디언 | 판매자 정보 페이지 공급사 정보 표시 검증 | 아코디언 "판매자 정보" 클릭으로 `/products/{id}/seller-info` 진입 상태 | 페이지 내용 확인 | 공급사 정보 표시 | P1 | REQ-PRODUCT-DETAIL-029 |  |
| TC-PRODUCT-DETAIL-060 | 상품상세 | 상세정보/아코디언 | 유의사항 페이지 배송·환불 안내 표시 검증 | 아코디언 "유의사항" 클릭으로 `/products/{id}/notice` 진입 상태 | 페이지 내용 확인 | 1. 배송 안내 표시(발송 지연 가능성, 배송지 변경 제한, 예약 상품 합배송 미지원 등)<br>2. 주문 취소 및 환불 안내 표시(자동 취소 조건, 일반/예약 상품별 취소 가능 시점, 환불 가능 기간) | P1 | REQ-PRODUCT-DETAIL-030 |  |
| TC-PRODUCT-DETAIL-061 | 상품상세 | 하단 찜 아이콘 | 찜 추가 후 찜 목록 반영 검증 | 1. 로그인<br>2. **[Production 데이터 변경]** 상품상세 하단 찜 아이콘 클릭으로 해당 상품을 찜한 상태(TC-PRODUCT-DETAIL-028 직후) | 내 스토어 > 찜 목록 내 "상품" 탭 확인 | 해당 상품 찜 목록 표시 | P0 | REQ-PRODUCT-DETAIL-034 |  |
| TC-PRODUCT-DETAIL-062 | 상품상세 | 하단 찜 아이콘 | 찜한 상품 아이콘 재클릭 찜 해제 토글 검증 | 1. 로그인<br>2. **[Production 데이터 변경]** 하단 찜 아이콘 클릭으로 해당 상품을 찜한 상태(보라색 하트)<br>3. 찜 동작 대표 TC: TC-WISHLIST-002 | 하단 찜 아이콘 재클릭 | 하트 아이콘 채워진 보라색 하트 → 빈 하트 변경 | P0 | REQ-PRODUCT-DETAIL-048 |  |
| TC-PRODUCT-DETAIL-063 | 상품상세 | 하단 찜 아이콘 | 찜 해제 후 새로고침 빈 하트 유지 검증 | 1. 로그인<br>2. **[Production 데이터 변경]** 하단 찜 아이콘 재클릭으로 찜을 해제한 상태 | 페이지 새로고침 | 새로고침 후 하단 하트 아이콘 빈 하트 유지 | P0 | REQ-PRODUCT-DETAIL-048 |  |
| TC-PRODUCT-DETAIL-064 | 상품상세 | 하단 찜 아이콘 | 찜 해제 후 찜 목록 제거 검증 | 1. 로그인<br>2. **[Production 데이터 변경]** 하단 찜 아이콘 재클릭으로 찜을 해제한 상태 | 내 스토어 > 찜 목록 내 "상품" 탭 확인 | 해당 상품 찜 목록 미표시 | P0 | REQ-PRODUCT-DETAIL-048 |  |
| TC-PRODUCT-DETAIL-065 | 상품상세 | 구매하기/옵션 선택 | 옵션 변경 시 옵션명·가격·총 금액 갱신 상태 전이 검증 | 1. 옵션 가격이 서로 다른 옵션 2개 이상이 선택 가능한 판매중 상품<br>2. 옵션 A 선택으로 "총 금액"이 옵션 A 가격 기준으로 표시된 상태 | 구매 영역 내 옵션 선택 재오픈 후 가격이 다른 옵션 B 클릭 | 1. 선택 옵션명, 옵션별 가격 옵션 B 기준 변경<br>2. "총 금액" 옵션 B 가격 기준 갱신 | P0 | REQ-PRODUCT-DETAIL-037 |  |
| TC-PRODUCT-DETAIL-066 | 상품상세 | 판매 상태별 버튼 | 예약구매 카운트다운 시간 경과 감소 검증 | 1. 예약구매 상태이며 예약 마감 전인 상품<br>2. 카운트다운 값 기록 상태 | 1분 이상 대기 후 카운트다운 표기 재확인 | 카운트다운 값 경과 시간만큼 감소 | P0 | REQ-PRODUCT-DETAIL-042 |  |
| TC-PRODUCT-DETAIL-067 | 상품상세 | 판매 상태별 버튼 | 판매종료 버튼 클릭 무반응 네거티브 검증 | 판매종료 상품 | 하단 "판매종료" 버튼 클릭 | 1. 구매 영역 확장, 옵션/수량 UI 노출, 팝업, 페이지 이동 없음<br>2. 화면 상태 클릭 전과 동일 | P0 | REQ-PRODUCT-DETAIL-045 |  |

## 1 Depth / 2 Depth 구성

| 1 Depth | 2 Depth | TC 개수 | 관련 TC ID |
|---|---|---|---|
| 상품상세 | 상품상세 진입 | 11 | TC-PRODUCT-DETAIL-001, TC-PRODUCT-DETAIL-002, TC-PRODUCT-DETAIL-003, TC-PRODUCT-DETAIL-005, TC-PRODUCT-DETAIL-006, TC-PRODUCT-DETAIL-043, TC-PRODUCT-DETAIL-044, TC-PRODUCT-DETAIL-045, TC-PRODUCT-DETAIL-046, TC-PRODUCT-DETAIL-047, TC-PRODUCT-DETAIL-048 |
| 상품상세 | 상단 바 | 5 | TC-PRODUCT-DETAIL-007, TC-PRODUCT-DETAIL-008, TC-PRODUCT-DETAIL-009, TC-PRODUCT-DETAIL-049, TC-PRODUCT-DETAIL-050 |
| 상품상세 | 이미지 캐러셀 | 4 | TC-PRODUCT-DETAIL-010, TC-PRODUCT-DETAIL-011, TC-PRODUCT-DETAIL-051, TC-PRODUCT-DETAIL-052 |
| 상품상세 | 작품명 | 2 | TC-PRODUCT-DETAIL-012, TC-PRODUCT-DETAIL-053 |
| 상품상세 | 상품 기본 정보 | 4 | TC-PRODUCT-DETAIL-013, TC-PRODUCT-DETAIL-015, TC-PRODUCT-DETAIL-054, TC-PRODUCT-DETAIL-055 |
| 상품상세 | 같은 작품 굿즈 | 4 | TC-PRODUCT-DETAIL-016, TC-PRODUCT-DETAIL-017, TC-PRODUCT-DETAIL-018, TC-PRODUCT-DETAIL-030 |
| 상품상세 | 상세정보/아코디언 | 10 | TC-PRODUCT-DETAIL-019, TC-PRODUCT-DETAIL-020, TC-PRODUCT-DETAIL-021, TC-PRODUCT-DETAIL-022, TC-PRODUCT-DETAIL-025, TC-PRODUCT-DETAIL-056, TC-PRODUCT-DETAIL-057, TC-PRODUCT-DETAIL-058, TC-PRODUCT-DETAIL-059, TC-PRODUCT-DETAIL-060 |
| 상품상세 | 하단 고정 영역 | 1 | TC-PRODUCT-DETAIL-026 |
| 상품상세 | 하단 찜 아이콘 | 6 | TC-PRODUCT-DETAIL-027, TC-PRODUCT-DETAIL-028, TC-PRODUCT-DETAIL-061, TC-PRODUCT-DETAIL-062, TC-PRODUCT-DETAIL-063, TC-PRODUCT-DETAIL-064 |
| 상품상세 | 구매하기/옵션 선택 | 6 | TC-PRODUCT-DETAIL-031, TC-PRODUCT-DETAIL-032, TC-PRODUCT-DETAIL-033, TC-PRODUCT-DETAIL-034, TC-PRODUCT-DETAIL-035, TC-PRODUCT-DETAIL-065 |
| 상품상세 | 판매 상태별 버튼 | 7 | TC-PRODUCT-DETAIL-036, TC-PRODUCT-DETAIL-037, TC-PRODUCT-DETAIL-038, TC-PRODUCT-DETAIL-039, TC-PRODUCT-DETAIL-040, TC-PRODUCT-DETAIL-066, TC-PRODUCT-DETAIL-067 |
| 상품상세 | 최근 본 상품 기록 | 1 | TC-PRODUCT-DETAIL-041 |
| 상품상세 | 로그인 상태별 화면 구성 | 1 | TC-PRODUCT-DETAIL-042 |

## 기법 적용 요약

PRD 명세 기반 블랙박스 기법(tc-writing Skill 1.6)을 기능 분류별로 적용했다. 상품상세는 입력값을 직접 입력하는 기능이 거의 없고(수량 조작, URL 직접 입력 정도), 대부분 조작·상태에 따라 결과가 달라지는 동작 기능이다.

| 기능 분류 | 입출력/동작 | 적용 기법 | 관련 TC ID |
|---|---|---|---|
| 입출력 | `/products/{상품번호}` URL 입력(존재 상품 / 존재하지 않는 상품 번호) | 정상 동작 / 네거티브 | 005(정상), 006(네거티브) |
| 입출력 | 수량 조작(최소 1개, 하한) | 경계값 | 035 |
| 입출력 | 상한(최대치) 명시 항목: 수량·캐러셀 사진 수·같은 작품 굿즈 카드 수·수량 뱃지 | 상한 경계값 3분리(초과/상한/미만) - PRD에 상한 수치 미명시로 TC 보류 | 없음(미결 질문 1, 2) |
| 입출력 | 이미지 캐러셀 첫/마지막 사진 순환 | 경계값 | 011, 052 |
| 입출력 | 이미지 캐러셀 일반 넘김·페이지네이션 | 정상 동작 | 010, 051 |
| 동작 | 옵션 유무·옵션 품절 여부에 따른 구매 영역(옵션 선택·수량 UI·총 금액) | 결정테이블(표 1) | 031, 032, 033, 034, 065 |
| 동작 | 상품 상태(판매중/예약구매/품절/판매종료)별 하단 버튼·찜 아이콘·버튼 클릭 | 결정테이블(표 2) | 036, 037, 038, 039, 040, 066, 067 |
| 동작 | 찜 on/off(비로그인·찜 안 함·찜 함) | 상태전이(표 3) | 027, 028, 061, 062, 063, 064, 030 |
| 동작 | 진입 경로별 상품상세 진입, 경로별 뒤로가기 | 유스케이스(경로별 흐름을 동작 단위로 분리) | 001, 043, 002, 044~047, 003, 048, 009, 050 |
| 동작 | 상단 바 이동, 작품명 이동, 같은 작품 굿즈, 아코디언 하위 페이지 이동·내용, 팝업 열기/닫기 | 유스케이스(동작 단위) | 007, 008, 049, 012, 053, 015, 055, 016~018, 021, 056~060, 022 |
| 동작 | 화면 구성·고정 영역·로그인 여부별 차이·최근 본 상품 | 유스케이스 + 로그인 여부 조건 비교 | 013, 054, 019, 020, 025, 026, 041, 042 |

### 표 1. 결정테이블 - 옵션 선택·구매 영역

| 조건/결과 | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| 옵션 유무 | 없음 | 있음 | 있음 | 있음(선택 상태에서 변경) |
| 클릭 대상 | "구매하기" | "구매하기" | 품절 옵션 | 가격이 다른 옵션 B |
| 옵션 드롭다운 | 미노출 | 먼저 펼침(품절 옵션은 회색+"품절" 라벨) | - | - |
| 수량선택 UI | 노출(수량 1) | (옵션 선택 후 노출) | 미표시 | 유지 |
| 옵션 선택/총 금액 | 총 금액 노출 | 옵션 A 선택 시 옵션별 가격, 총 금액 A 기준 | 선택 불가, 총 금액 변경 없음 | 옵션명·가격 B 기준, 총 금액 B 기준 갱신 |
| 관련 TC | 031 | 032, 034 | 033 | 065 |

### 표 2. 결정테이블 - 상품 상태별 하단 버튼

| 조건/결과 | 판매중 | 예약구매(마감 전) | 품절 | 판매종료 |
|---|---|---|---|---|
| 하단 버튼 텍스트 | "구매하기" | "예약구매" | "품절" | "판매종료" |
| 버튼 활성 여부 | 활성(보라색) | 활성(보라색) | 비활성(회색조) | 비활성(회색조) |
| 카운트다운 | 없음 | "예약 마감까지 D일 HH:MM"(이미지·버튼, 시간 경과 시 감소) | 없음 | 없음 |
| 찜 아이콘 | (찜 동작은 표 3) | (찜 동작은 표 3) | 활성 | 활성 |
| 버튼 클릭 결과 | 구매 영역 확장(TC-031, 032) | PRD 미명시(TC 없음, 미결 질문) | 무반응(구매 영역·팝업·이동 없음) | 무반응(구매 영역·팝업·이동 없음) |
| 관련 TC | 036 | 037, 066 | 038, 040 | 039, 067 |

### 표 3. 상태전이 - 찜 on/off

| 현재 상태 | 이벤트 | 다음 상태 | 관찰 결과 | 관련 TC |
|---|---|---|---|---|
| 비로그인(찜 불가) | 하단 찜 아이콘 클릭 | 비로그인 유지(빈 하트) | 로그인 유도 팝업, 찜 토스트 미표시 (무효 전이) | 027 |
| 로그인, 찜 off(빈 하트) | 하단 찜 아이콘 클릭 | 찜 on(보라색 하트) | "찜한 상품에 추가했어요" 토스트, 찜 목록에 상품 표시 | 028, 061 |
| 로그인, 찜 on(보라색 하트) | 하단 찜 아이콘 재클릭 | 찜 off(빈 하트) | 하트 빈 하트 변경 | 062 |
| 찜 off(해제 직후) | 페이지 새로고침 | 찜 off 유지 | 빈 하트 유지 | 063 |
| 찜 off(해제 직후) | 내 스토어 > 찜 목록 확인 | 찜 off 유지 | 찜 목록에서 해당 상품 제거 | 064 |
| 로그인, "같은 작품 굿즈" 카드 찜 off | 카드 찜 아이콘 클릭 | 해당 카드 찜 on | 상세 미이동, 토스트 노출, 카드 하트 보라색 | 030 |

## Priority 산정 근거

Risk 스프레드시트 `리스크 매트릭스`의 RI-PRODUCT-DETAIL-001~012 Likelihood/Impact/Risk Score는 사용자가 확정한 값이므로 Priority 산정의 우선 근거로 사용한다(Skill 3절). 매핑된 RI의 Risk Score를 Priority 매핑표(P0 16~25 / P1 9~15 / P2 1~8)에 적용했으며, 동일 RI의 TC는 동일 Priority를 유지한다. 별도 보정한 TC는 없다(revised2와 동일한 RI 매핑, Priority 변경 없음).

| RI-ID | 리스크 아이템 | Likelihood | Impact | Risk Score | 레벨 | Priority |
|---|---|---|---|---|---|---|
| RI-PRODUCT-DETAIL-001 | 상품상세 진입 경로 및 에러 페이지 | 3 | 3 | 9 | Medium | P1 |
| RI-PRODUCT-DETAIL-002 | 상단 바 아이콘 및 뒤로가기 동작 | 3 | 3 | 9 | Medium | P1 |
| RI-PRODUCT-DETAIL-003 | 이미지 캐러셀 순환 및 페이지네이션 | 3 | 3 | 9 | Medium | P1 |
| RI-PRODUCT-DETAIL-004 | 작품명·상품정보·배송정보 표시 | 3 | 4 | 12 | Medium | P1 |
| RI-PRODUCT-DETAIL-005 | 같은 작품 굿즈 추천 캐러셀 | 3 | 3 | 9 | Medium | P1 |
| RI-PRODUCT-DETAIL-006 | 상세정보 탭 콘텐츠 및 더보기 | 3 | 3 | 9 | Medium | P1 |
| RI-PRODUCT-DETAIL-007 | 아코디언 하위 페이지 이동 및 내용 | 3 | 3 | 9 | Medium | P1 |
| RI-PRODUCT-DETAIL-008 | 공통 푸터 노출 | 2 | 2 | 4 | Low | P2 |
| RI-PRODUCT-DETAIL-009 | 하단 찜 아이콘 동작 | 4 | 4 | 16 | High | P0 |
| RI-PRODUCT-DETAIL-010 | 옵션·수량 선택 및 금액 갱신 | 4 | 5 | 20 | High | P0 |
| RI-PRODUCT-DETAIL-011 | 상품 상태별 하단 버튼 표시 | 4 | 5 | 20 | High | P0 |
| RI-PRODUCT-DETAIL-012 | 로그인 여부별 화면 차이 | 3 | 3 | 9 | Medium | P1 |

- **TC-PRODUCT-DETAIL-001, 002, 003, 005, 006, 043~048**: Impact 3 / Likelihood 3 / Risk Score 9 - RI-PRODUCT-DETAIL-001 (Medium, P1). 진입 경로별 동작 TC(배너, 메인 리스트, 내 스토어 3개 섹션, 찜 2개 탭, 장바구니, 주문내역, URL 직접, 404 예외)
- **TC-PRODUCT-DETAIL-007~009, 049, 050**: Impact 3 / Likelihood 3 / Risk Score 9 - RI-PRODUCT-DETAIL-002 (Medium, P1). 아이콘 표시, 검색/장바구니 아이콘 이동, 진입 경로별 뒤로가기
- **TC-PRODUCT-DETAIL-010, 011, 051, 052**: Impact 3 / Likelihood 3 / Risk Score 9 - RI-PRODUCT-DETAIL-003 (Medium, P1). 011·052는 순환 경계값
- **TC-PRODUCT-DETAIL-012, 013, 015, 053~055**: Impact 4 / Likelihood 3 / Risk Score 12 - RI-PRODUCT-DETAIL-004 (Medium, P1)
- **TC-PRODUCT-DETAIL-016~018, 030**: Impact 3 / Likelihood 3 / Risk Score 9 - RI-PRODUCT-DETAIL-005 (Medium, P1). 030(REQ-049)은 리스크 아이템 시트가 RI-005에 매핑한 항목이라 RI-005 기준으로 산정(이전: RI-009 P0)
- **TC-PRODUCT-DETAIL-019, 020**: Impact 3 / Likelihood 3 / Risk Score 9 - RI-PRODUCT-DETAIL-006 (Medium, P1)
- **TC-PRODUCT-DETAIL-021, 022, 056~060**: Impact 3 / Likelihood 3 / Risk Score 9 - RI-PRODUCT-DETAIL-007 (Medium, P1)
- **TC-PRODUCT-DETAIL-025**: Impact 2 / Likelihood 2 / Risk Score 4 - RI-PRODUCT-DETAIL-008 (Low, P2)
- **TC-PRODUCT-DETAIL-026, 027, 028, 061~064**: Impact 4 / Likelihood 4 / Risk Score 16 - RI-PRODUCT-DETAIL-009 (High, P0). 비로그인 분기(027), 추가(028)·찜 목록 반영(061)·해제(062)·새로고침 유지(063)·찜 목록 제거(064) 동작별 구성(표 3 상태전이). 026(하단 고정 영역)은 매트릭스상 별도 항목이 없어 찜 아이콘이 위치한 하단 영역으로 RI-009에 매핑함(원본·revised·revised2와 동일, 확인 필요)
- **TC-PRODUCT-DETAIL-031~035, 065**: Impact 5 / Likelihood 4 / Risk Score 20 - RI-PRODUCT-DETAIL-010 (High, P0). 옵션 유/무 분기, 품절 옵션 Negative, 옵션 A 선택·B 변경 시 금액 갱신, 수량 최소 경계(표 1 결정테이블)
- **TC-PRODUCT-DETAIL-036~040, 066, 067**: Impact 5 / Likelihood 4 / Risk Score 20 - RI-PRODUCT-DETAIL-011 (High, P0). 4가지 상품 상태별 버튼 표시, 카운트다운 감소, 비활성 버튼(품절/판매종료) Negative 클릭(표 2 결정테이블)
- **TC-PRODUCT-DETAIL-041, 042**: Impact 3 / Likelihood 3 / Risk Score 9 - RI-PRODUCT-DETAIL-012 (Medium, P1)

## 상한 항목 점검 결과 (Skill 1.6 상한 항목 경계값 분리)

PRD(`prd-product-detail.md`) 전체에서 최대치(상한 N)가 명시된 항목을 추출했다. 상한 초과 / 상한(정확히 N) / 상한 미만 3개 TC 분리는 **PRD에 상한 수치가 고정되어 있고 정확히 N개·N-1개 데이터를 확보할 수 있을 때만** 작성하며, 그렇지 않은 항목은 TC를 임의로 만들지 않고 보류했다.

| 항목 | PRD 근거 | 상한 N | 초과 / 상한 / 미만 TC ID | 보류 사유 |
|---|---|---|---|---|
| 구매 수량 | REQ-039 "최대 수량은 상품마다 상이하여 특정하지 않음" | 미정(상품별 상이) | 없음 / 없음 / 없음 | 상한 수치가 PRD에 고정되어 있지 않고 초과 시 기대 결과도 PRD에 없음 |
| 이미지 캐러셀 사진 수 | REQ-013~015 ("N/M" 형식, 예시 "1/4"만 있음) | 미명시 | 없음 / 없음 / 없음 | 최대 사진 수가 PRD에 명시되지 않음(예시 값은 상한이 아님) |
| "같은 작품 굿즈" 캐러셀 표시 카드 수 | REQ-020 ("나열"만 명시) | 미명시 | 없음 / 없음 / 없음 | 표시 최대 개수가 PRD에 명시되지 않음 |
| 장바구니 아이콘 수량 뱃지 | REQ-009 ("담긴 수량 뱃지") | 미명시 | 없음 / 없음 / 없음 | 뱃지 표시 최대값이 PRD에 명시되지 않음 |

- 수량 최소값 1(REQ-039)은 하한이며 기존 TC-PRODUCT-DETAIL-035(최소 수량 1에서 감소 불가)로 이미 경계값을 검증한다. 상한 항목이 아니므로 3개 분리 대상이 아니다.
- 상한 수치가 PRD에 추가되면(미결 질문 1~3) 해당 항목마다 초과/상한/미만 TC 3개를 신규 번호(068부터)로 추가한다.

## 미결 질문

1. 구매 수량의 최대 수량(상품별 상이)은 어떻게 확정할지, 상한 수량 초과 시 기대 결과(차단/오류 문구 등)는 무엇인지 PRD에 명시가 필요하다. 확정 전에는 수량 상한 TC(초과/상한/미만)를 작성하지 않았다.
2. 이미지 캐러셀 최대 사진 수, "같은 작품 굿즈" 캐러셀 표시 최대 카드 수, 장바구니 수량 뱃지 표시 최대값이 존재하는지 PRD에 명시가 필요하다. 존재한다면 정확히 N장/N개 및 N-1장/N-1개 데이터를 가진 상품(또는 계정 상태) 확보 방법도 필요하다.
3. 예약구매 상태에서 "예약구매" 버튼 클릭 시 결과가 PRD에 명시되어 있지 않아 TC를 만들지 않았다(표 2 참조, revised3에서 유지).
4. 상품상세 URL 직접 진입(이전 화면 없음) 후 뒤로가기의 이동 위치가 PRD에 없어 TC를 만들지 않았다(revised3에서 유지).
5. 찜 추가/해제·로그인 유도 팝업 관련 TC(TC-PRODUCT-DETAIL-027, 028, 030, 061~064)는 `docs/tc/wishlist.md`와 겹칠 수 있는 후보이다. 이번에도 정리하지 않고 동작 기준으로 유지했으며 정리 여부는 사용자 결정이 필요하다(revised3에서 유지).
6. TC-PRODUCT-DETAIL-026(하단 고정 영역)은 Risk Matrix에 별도 항목이 없어 RI-PRODUCT-DETAIL-009에 매핑했다(revised3에서 유지, 확인 필요).
7. `[Production 데이터 변경]` 표기 TC(028, 030, 041, 061~064)는 실행 전 사용자 승인이 필요하다(revised3에서 유지).

## 이전 ID 매핑 (revised4 → revised5)

| revised4 ID | revised5 처리 |
|---|---|
| TC-PRODUCT-DETAIL-001~003, 005~013, 015~022, 025~028, 030~067 (revised4의 전체 62건) | 전체 동일(ID·Priority·내용 유지, 번호 표기만 변경) |
| 분리 | 없음 |
| 신규 | 없음 |
| 결번 | 004, 014, 023, 024, 029는 계속 결번(재사용 없음). 다음 신규 번호는 068부터 |

## 변경 이력

| 날짜 | 변경 사유 | 상태 |
|---|---|---|
| 2026-10-21 | `docs/tc/revised/product-detail.md`(37건)를 tc-writing Skill 개정 규칙(1.3 동작 단위 세분화, 1.4, 4.1, 4.7)에 따라 동작 단위로 재작성(62건, revised2) | 초안 |
| 2026-10-21 | revised2(62건)를 Skill 1.5 표기 규칙과 1.6 설계 기법(기법 적용 요약, 결정테이블·상태전이 표)으로 재작성(62건, revised3) | 초안 |
| 2026-10-21 | revised3(62건)를 Skill 1.6 상한 항목 경계값 분리 규칙으로 점검해 재작성(revised4). PRD에 고정된 상한 수치가 없어 분리·신규 TC 없음(62건 유지), 상한 항목 점검 결과·미결 질문 추가. 기존 문서·Spreadsheet 미수정, Spreadsheet 미반영 | 초안 |
| 2026-10-21 | revised4(62건)를 Skill 1.5 표기 규칙(복수 항목 `1.` `2.` 번호 + `<br>`, `1)` 형식 폐기, Preconditions 독립 조건 분리)으로 재작성(revised5). 표기 형식만 변경, ID·Priority·내용·62건 유지. 기존 문서·Spreadsheet 미수정, Spreadsheet 미반영 | 초안 |
| 2026-10-22 | `docs/tc/revised5/product-detail.md`(62건)를 새 컬럼 구조(1 Depth / 2 Depth 도입, Requirement ID Priority 뒤로 이동)로 변환(revised6). 값·행 구성은 revised5와 동일. 기존 문서·Spreadsheet 미변경 | 초안 |
| 2026-10-22 | `docs/tc/revised6/product-detail.md`(62건)의 Test Scenario를 3 Depth(테스트 시나리오/목적)로 변환(revised7). 다른 컬럼 값·행 구성은 revised6와 동일. 기존 문서·Spreadsheet 미변경 | 초안 |
| 2026-10-22 | Priority 재산정(리스크 시트 확정 점수·REQ 매핑 기준 전수 대조). TC-PRODUCT-DETAIL-030을 RI-009(P0)에서 시트 매핑인 RI-005(Score 9)로 정정해 P0→P1 변경. 나머지 TC는 변경 없음. Spreadsheet 미반영 | 초안 |
