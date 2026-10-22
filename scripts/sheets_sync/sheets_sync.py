#!/usr/bin/env python3
"""
Google Spreadsheet 동기화 CLI.

tc-writing Skill(.claude/skills/tc-writing/SKILL.md)의 10개 컬럼 정의를 따르는
Markdown TC 문서(docs/tc/{feature-slug}.md)를 읽어 Google Spreadsheet에 반영한다.

지원 명령:
  list                        : 현재 Spreadsheet에 저장된 TC 목록을 조회한다.
  append                      : Markdown TC 문서의 TC를 Spreadsheet에 추가한다(append-only, 수정/삭제 없음).
  pull                        : 시트의 TC를 읽어 Markdown TC 문서에 반영한다(시트→md, 시트는 수정하지 않음).
  candidate-create-worksheet  : 자동화 후보 평가용 워크시트를 생성한다(이미 있으면 오류).
  candidate-sync              : Candidate 문서(docs/tc/automation-candidates/{slug}.md)의
                                 AI 작성 영역만 Spreadsheet에 반영한다(신규 TC는 새 행 추가,
                                 기존 TC는 AI 컬럼만 갱신. QA Decision/QA Comment는 건드리지 않음).
  candidate-list               : 자동화 후보 워크시트를 조회한다(QA Decision/QA Comment 포함).
  risk-list                   : Feature Risk Matrix(별도 스프레드시트, 읽기 전용)를 조회한다.
  regression-list             : 전체 TC 워크시트에서 "Regression 여부"가 "O"인 TC를 읽기 전용으로 조회한다.
  regression-create           : 전체 TC 워크시트에서 사용자가 "Regression 여부"를 "O"로 입력한 TC만
                                 모아 새 Regression 워크시트를 생성한다(원본 시트는 수정하지 않음).

이 스크립트는 tc-agent / automation-candidate-agent가 Bash로 호출하는 용도로만 설계되었으며,
행 수정(update)이 필요한 candidate-sync를 제외하면 기존 행을 수정하거나 삭제하는 기능은
의도적으로 제공하지 않는다(README.md 참조). candidate-sync조차 AI 작성 영역 컬럼 범위로만
쓰기가 제한되며, 사용자 작성 영역(QA Decision/QA Comment)은 절대 덮어쓰지 않는다.
"Regression 여부" 열도 사용자 입력 영역이며, 이 스크립트는 이 열에 값을 쓰지 않는다(항상 빈 값).
"""

import argparse
import os
import re
import sys

TC_COLUMNS = [
    "ID",
    "1 Depth",
    "2 Depth",
    "3 Depth",
    "Preconditions",
    "Test Steps",
    "Expected Result",
    "Priority",
    "Requirement ID",
    "Result",
]

DEFAULT_WORKSHEET_NAME = "TC"

# Spreadsheet의 전체 TC 워크시트는 TC 컬럼 10개 뒤에 사용자 입력 전용 "Regression 여부" 열을 갖는다.
# Markdown TC 문서의 표는 10개 컬럼(TC_COLUMNS)만 사용하며, 이 열은 Sheet에서만 존재한다.
# AI는 이 열에 값을 쓰지 않는다(사용자가 O/X를 직접 입력, "O"만 Regression TC로 사용).
REGRESSION_COLUMN = "Regression 여부"
SHEET_TC_COLUMNS = TC_COLUMNS + [REGRESSION_COLUMN]

DEFAULT_REGRESSION_WORKSHEET_NAME = "Regression TC"

# Feature Risk Matrix는 TC용 스프레드시트와 별도 파일이며(GOOGLE_RISK_SHEET_ID), 읽기 전용으로만 조회한다.
# 시트 상단에 제목 행이 있어 실제 헤더는 5행이다.
DEFAULT_RISK_WORKSHEET_NAME = "리스크 매트릭스"
DEFAULT_RISK_HEADER_ROW = 5

# automation-candidate-agent.md 산출물 템플릿의 "AI 평가 결과" 표 헤더와 정확히 일치해야 한다.
CANDIDATE_AI_COLUMNS = [
    "TC ID",
    "Business Criticality",
    "Regression Frequency",
    "Automation Stability",
    "Result Determinism",
    "Manual Test Cost",
    "Maintenance Cost",
    "Automation Score",
    "Candidate (AI)",
    "선정/제외 사유",
]

# 사용자(QA)가 Google Sheet에서 직접 입력하는 영역. AI는 이 컬럼을 절대 쓰지 않는다.
CANDIDATE_QA_COLUMNS = ["QA Decision", "QA Comment"]

CANDIDATE_FULL_COLUMNS = CANDIDATE_AI_COLUMNS + CANDIDATE_QA_COLUMNS

DEFAULT_CANDIDATE_WORKSHEET_NAME = "Automation Candidates"


def load_env():
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass


def get_client_and_sheet(sheet_id_env="GOOGLE_SHEET_ID"):
    load_env()

    service_account_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
    sheet_id = os.environ.get(sheet_id_env)

    missing = []
    if not service_account_file:
        missing.append("GOOGLE_SERVICE_ACCOUNT_FILE")
    if not sheet_id:
        missing.append(sheet_id_env)
    if missing:
        print(
            "[오류] 다음 환경변수가 설정되어 있지 않습니다: " + ", ".join(missing),
            file=sys.stderr,
        )
        print(
            "설정 방법은 scripts/sheets_sync/README.md를 참고하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    if not os.path.isfile(service_account_file):
        print(
            f"[오류] GOOGLE_SERVICE_ACCOUNT_FILE 경로에 파일이 없습니다: {service_account_file}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        import gspread
    except ImportError:
        print(
            "[오류] gspread 패키지가 설치되어 있지 않습니다. "
            "scripts/sheets_sync/README.md의 설치 안내를 참고하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        gc = gspread.service_account(filename=service_account_file)
        sh = gc.open_by_key(sheet_id)
    except Exception as exc:  # noqa: BLE001 - CLI 최상위 예외를 사용자에게 그대로 보고
        print(f"[오류] Google Sheets 연결에 실패했습니다: {exc}", file=sys.stderr)
        sys.exit(1)

    return gc, sh


def get_or_create_worksheet(sh, create_if_missing, worksheet_name=None, columns=None, default_name=DEFAULT_WORKSHEET_NAME):
    columns = columns or SHEET_TC_COLUMNS
    worksheet_name = worksheet_name or os.environ.get("GOOGLE_SHEET_WORKSHEET", default_name)
    try:
        ws = sh.worksheet(worksheet_name)
        return ws, worksheet_name, False
    except Exception:  # noqa: BLE001 - gspread.WorksheetNotFound 등
        if not create_if_missing:
            return None, worksheet_name, False
        ws = sh.add_worksheet(title=worksheet_name, rows=1000, cols=len(columns))
        ws.append_row(columns, value_input_option="USER_ENTERED")
        return ws, worksheet_name, True


def column_letter(index):
    """1-based 컬럼 인덱스를 스프레드시트 컬럼 문자로 변환한다 (1 -> A, 27 -> AA)."""
    letters = ""
    while index > 0:
        index, remainder = divmod(index - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return letters


def split_table_row(line):
    """마크다운 테이블 한 행을 셀 리스트로 분리한다 (이스케이프된 '\\|' 는 리터럴 '|' 로 처리)."""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    raw_cells = re.split(r"(?<!\\)\|", line)
    return [cell.replace("\\|", "|").strip() for cell in raw_cells]


def is_separator_row(cells):
    return all(re.fullmatch(r":?-{2,}:?", cell.strip()) for cell in cells if cell.strip() != "") and any(
        cell.strip() for cell in cells
    )


def find_table_rows(lines, expected_header):
    """줄 리스트에서 expected_header와 정확히 일치하는 헤더를 가진 표를 모두 찾아
    (표 번호, 줄 인덱스, 셀 리스트) 목록을 반환한다. 줄 인덱스는 lines 기준 0-based다."""
    found = []
    table_no = 0
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.strip().startswith("|"):
            header_cells = split_table_row(line)
            if header_cells == expected_header:
                # 다음 줄은 구분선(---) 이어야 함
                if i + 1 < n and lines[i + 1].strip().startswith("|"):
                    sep_cells = split_table_row(lines[i + 1])
                    if is_separator_row(sep_cells):
                        j = i + 2
                        while j < n and lines[j].strip().startswith("|"):
                            data_cells = split_table_row(lines[j])
                            if len(data_cells) == len(expected_header):
                                found.append((table_no, j, data_cells))
                            j += 1
                        table_no += 1
                        i = j
                        continue
        i += 1
    return found


def parse_markdown_tables(markdown_text, expected_header):
    """Markdown 문서에서 expected_header와 정확히 일치하는 헤더를 가진 표를 모두 찾아
    데이터 행을 합쳐 반환한다(문서 안에 같은 형식의 표가 여러 개 있어도 모두 수집)."""
    found = find_table_rows(markdown_text.splitlines(), expected_header)
    return [dict(zip(expected_header, cells)) for _, _, cells in found]


def parse_tc_tables(markdown_text):
    """Markdown 문서에서 TC 컬럼 정의(10개 컬럼)와 일치하는 표를 모두 찾아 데이터 행을 합쳐 반환한다."""
    return parse_markdown_tables(markdown_text, TC_COLUMNS)


def parse_candidate_ai_table(markdown_text):
    """Markdown 문서에서 Candidate "AI 평가 결과" 표(10개 컬럼)와 일치하는 표를 찾아 반환한다."""
    return parse_markdown_tables(markdown_text, CANDIDATE_AI_COLUMNS)


def feature_worksheet_name(feature_slug):
    """Feature slug를 Feature별 TC 워크시트 이름으로 변환한다. 'search' -> 'Testcase_Search',
    'product-detail' -> 'Testcase_Product_Detail'."""
    parts = [part for part in re.split(r"[-_\s]+", feature_slug.strip()) if part]
    if not parts:
        print("[오류] Feature slug가 비어 있어 워크시트 이름을 만들 수 없습니다.", file=sys.stderr)
        sys.exit(1)
    return "Testcase_" + "_".join(part.capitalize() for part in parts)


def worksheet_name_from_input(input_path):
    """docs/tc/{feature-slug}.md 경로에서 Feature별 워크시트 이름을 만든다."""
    return feature_worksheet_name(os.path.splitext(os.path.basename(input_path))[0])


def cmd_list(args):
    _, sh = get_client_and_sheet()
    worksheet = args.worksheet or (feature_worksheet_name(args.feature) if args.feature else None)
    ws, worksheet_name, created = get_or_create_worksheet(
        sh, create_if_missing=False, worksheet_name=worksheet
    )

    if ws is None:
        print(f"워크시트 '{worksheet_name}'가 아직 없습니다. 반영된 TC가 없습니다.")
        return

    values = ws.get_all_values()
    if not values:
        print(f"워크시트 '{worksheet_name}'에 데이터가 없습니다.")
        return

    header = values[0]
    data_rows = values[1:]

    if args.ids_only:
        id_col = header.index("ID") if "ID" in header else 0
        for row in data_rows:
            if len(row) > id_col and row[id_col].strip():
                print(row[id_col].strip())
        return

    print(f"워크시트: {worksheet_name} (총 {len(data_rows)}건)")
    print("| " + " | ".join(header) + " |")
    print("|" + "|".join(["---"] * len(header)) + "|")
    for row in data_rows:
        padded = row + [""] * (len(header) - len(row))
        print("| " + " | ".join(padded[: len(header)]) + " |")


def cmd_append(args):
    if not os.path.isfile(args.input):
        print(f"[오류] 입력 파일을 찾을 수 없습니다: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    new_rows = parse_tc_tables(markdown_text)
    if not new_rows:
        print(
            f"[오류] {args.input} 에서 TC 컬럼 정의와 일치하는 표를 찾지 못했습니다.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 입력 파일 내 ID 중복 검사
    seen = {}
    dups_in_file = []
    for row in new_rows:
        tc_id = row["ID"]
        if tc_id in seen:
            dups_in_file.append(tc_id)
        seen[tc_id] = True
    if dups_in_file:
        print(
            "[오류] 입력 파일 내에 중복된 TC ID가 있습니다: " + ", ".join(sorted(set(dups_in_file))),
            file=sys.stderr,
        )
        sys.exit(1)

    _, sh = get_client_and_sheet()
    ws, worksheet_name, created = get_or_create_worksheet(
        sh, create_if_missing=not args.dry_run,
        worksheet_name=args.worksheet or worksheet_name_from_input(args.input),
    )

    existing_ids = set()
    need_header_write = False
    if ws is not None:
        values = ws.get_all_values()
        is_fully_blank = not values or all(
            all(cell.strip() == "" for cell in row) for row in values
        )
        if is_fully_blank:
            # 완전히 빈 워크시트(사용자가 이름만 미리 만들어 둔 경우 포함) — 헤더가 없을 뿐이므로
            # 안전하게 헤더를 새로 쓴다. 데이터가 섞여 있는 상태는 아래 else 분기에서 그대로 검증한다.
            need_header_write = True
        else:
            header = values[0]
            if header != SHEET_TC_COLUMNS:
                print(
                    "[오류] 기존 워크시트의 헤더가 TC 컬럼 정의('Regression 여부' 열 포함 11개)와 다릅니다. "
                    "시트를 임의로 덮어쓰지 않고 중단합니다.",
                    file=sys.stderr,
                )
                print(f"  기존 헤더: {header}", file=sys.stderr)
                print(f"  기대 헤더: {SHEET_TC_COLUMNS}", file=sys.stderr)
                print(
                    "이전 형식(Feature 컬럼 등 다른 컬럼 구성)의 TC가 남아 있는 워크시트라면 사용하지 말고, "
                    "새 워크시트 이름을 --worksheet로 지정하세요.",
                    file=sys.stderr,
                )
                sys.exit(1)
            id_col = header.index("ID")
            for row in values[1:]:
                if len(row) > id_col and row[id_col].strip():
                    existing_ids.add(row[id_col].strip())

    conflict_ids = [row["ID"] for row in new_rows if row["ID"] in existing_ids]
    if conflict_ids:
        print(
            "[오류] 이미 Spreadsheet에 존재하는 TC ID와 충돌합니다(append는 기존 행을 "
            "수정/삭제하지 않으므로 중단합니다): " + ", ".join(sorted(set(conflict_ids))),
            file=sys.stderr,
        )
        print(
            "기존 TC를 수정해야 하는 경우 사용자와 함께 반영 방법을 결정하세요 "
            "(README.md '승인완료 문서 재수정 시 처리' 참고).",
            file=sys.stderr,
        )
        sys.exit(1)

    if ws is None:
        sheet_note = " (신규 생성 예정)"
    elif need_header_write:
        sheet_note = " (기존 빈 워크시트, 헤더 신규 작성 예정)"
    else:
        sheet_note = ""

    print(f"입력 파일: {args.input}")
    print(f"대상 워크시트: {worksheet_name}{sheet_note}")
    print(f"추가될 TC 수: {len(new_rows)}건")
    print("추가될 TC ID: " + ", ".join(row["ID"] for row in new_rows))

    if args.dry_run:
        print("\n[dry-run] 실제로 Spreadsheet에 반영하지 않았습니다.")
        return

    if need_header_write:
        ws.update(range_name="A1", values=[SHEET_TC_COLUMNS])

    # "Regression 여부" 열은 사용자 입력 영역이므로 항상 빈 값으로 추가한다.
    # md 표 셀의 <br>은 시트에서 실제 줄바꿈으로 변환해 쓴다(pull은 반대로 줄바꿈을 <br>로 되돌린다).
    rows_to_append = [[to_sheet_cell(row[col]) for col in TC_COLUMNS] + [""] for row in new_rows]
    ws.append_rows(rows_to_append, value_input_option="USER_ENTERED")
    if created or need_header_write:
        # 새로 만든 워크시트에만 줄바꿈 표시(텍스트 줄바꿈)를 설정한다. 실패해도 반영 결과에는 영향이 없다.
        try:
            ws.format("D:G", {"wrapStrategy": "WRAP", "verticalAlignment": "TOP"})
        except Exception as exc:  # noqa: BLE001 - 서식 실패는 경고만 출력
            print(f"[경고] 줄바꿈 서식 설정에 실패했습니다(데이터 반영은 완료): {exc}", file=sys.stderr)
    print(f"\n{len(rows_to_append)}건을 워크시트 '{worksheet_name}'에 추가했습니다.")


def to_sheet_cell(value):
    """Markdown 표 셀 값을 시트에 쓸 문자열로 바꾼다(<br> 계열 태그를 실제 줄바꿈으로 치환)."""
    return re.sub(r"\s*<br\s*/?>\s*", "\n", value, flags=re.IGNORECASE)


def normalize_sheet_cell(value):
    """시트 셀 값을 Markdown 표 셀 비교용 문자열로 바꾼다(줄바꿈은 <br>로 치환)."""
    return re.sub(r"\s*\r?\n\s*", "<br>", value.strip())


def format_table_row(cells):
    """셀 리스트를 Markdown 표 한 행으로 만든다('|' 는 '\\|' 로 이스케이프)."""
    line = "| " + " | ".join(cell.replace("|", "\\|") for cell in cells) + " |"
    # 빈 셀은 기존 문서 표기("| |")와 맞춘다.
    while "|  |" in line:
        line = line.replace("|  |", "| |")
    return line


def tc_id_prefix(tc_id):
    """'TC-SEARCH-005' -> 'TC-SEARCH' (Feature 구분용 접두어)."""
    return re.sub(r"-\d+$", "", tc_id)


def cmd_pull(args):
    """시트의 TC를 읽어 Markdown TC 문서에 반영한다(시트→md). 시트에는 쓰지 않는다."""
    if not os.path.isfile(args.input):
        print(f"[오류] 입력 파일을 찾을 수 없습니다: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        lines = f.read().split("\n")

    md_rows = find_table_rows(lines, TC_COLUMNS)
    if not md_rows:
        print(
            f"[오류] {args.input} 에서 TC 컬럼 정의와 일치하는 표를 찾지 못했습니다.",
            file=sys.stderr,
        )
        sys.exit(1)

    md_by_id = {}
    for _, line_index, cells in md_rows:
        md_by_id[cells[0]] = (line_index, cells)
    prefixes = {tc_id_prefix(tc_id) for tc_id in md_by_id}

    _, sh = get_client_and_sheet()
    ws, worksheet_name, _ = get_or_create_worksheet(
        sh, create_if_missing=False,
        worksheet_name=args.worksheet or worksheet_name_from_input(args.input),
    )
    if ws is None:
        print(f"[오류] 워크시트 '{worksheet_name}'가 없습니다. 먼저 append로 반영하세요.", file=sys.stderr)
        sys.exit(1)

    try:
        values = ws.get_all_values()
    except Exception as exc:  # noqa: BLE001 - API 오류를 사용자에게 그대로 보고
        print(f"[오류] 워크시트 '{worksheet_name}' 조회에 실패했습니다: {exc}", file=sys.stderr)
        sys.exit(1)

    if not values or values[0] != SHEET_TC_COLUMNS:
        print(
            "[오류] 워크시트 헤더가 TC 컬럼 정의('Regression 여부' 열 포함 11개)와 다릅니다.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 시트 행 수집: 같은 Feature(ID 접두어)의 행만 대상으로 한다. "Regression 여부" 열은 제외한다.
    sheet_by_id = {}
    ignored_other_feature = 0
    for row in values[1:]:
        padded = row + [""] * (len(SHEET_TC_COLUMNS) - len(row))
        tc_id = padded[0].strip()
        if not tc_id:
            continue
        if tc_id_prefix(tc_id) not in prefixes:
            ignored_other_feature += 1
            continue
        if tc_id in sheet_by_id:
            print(f"[오류] 시트에 중복된 TC ID가 있습니다: {tc_id}", file=sys.stderr)
            sys.exit(1)
        sheet_by_id[tc_id] = [normalize_sheet_cell(c) for c in padded[: len(TC_COLUMNS)]]

    changed = []
    for tc_id, (line_index, md_cells) in md_by_id.items():
        if tc_id not in sheet_by_id:
            continue
        sheet_cells = sheet_by_id[tc_id]
        diff_cols = [col for col, a, b in zip(TC_COLUMNS, md_cells, sheet_cells) if a != b]
        if diff_cols:
            changed.append((tc_id, line_index, sheet_cells, diff_cols))
    sheet_only = [tc_id for tc_id in sheet_by_id if tc_id not in md_by_id]
    md_only = [tc_id for tc_id in md_by_id if tc_id not in sheet_by_id]

    print(f"입력 파일: {args.input}")
    print(f"워크시트: {worksheet_name} (같은 Feature 행 {len(sheet_by_id)}건, 다른 Feature 행 {ignored_other_feature}건 제외)")
    print(f"\n[수정됨] {len(changed)}건 (시트 값으로 md 갱신)")
    for tc_id, _, _, diff_cols in changed:
        print(f"- {tc_id}: {', '.join(diff_cols)}")
    print(f"\n[시트에만 있음] {len(sheet_only)}건 (md 첫 TC 표 끝에 추가)")
    for tc_id in sheet_only:
        print(f"- {tc_id}")
    print(f"\n[md에만 있음] {len(md_only)}건 (자동 삭제하지 않음, 시트에서 삭제된 것인지 확인 필요)")
    for tc_id in md_only:
        print(f"- {tc_id}")

    if not changed and not sheet_only:
        print("\n반영할 변경이 없습니다.")
        return

    if args.dry_run:
        print("\n[dry-run] md 파일을 수정하지 않았습니다.")
        return

    for _, line_index, sheet_cells, _ in changed:
        lines[line_index] = format_table_row(sheet_cells)

    if sheet_only:
        # 첫 번째 TC 표의 마지막 행 뒤에 추가한다(줄 번호 이동을 막기 위해 변경 반영 후 마지막에 삽입).
        first_table_last = max(idx for no, idx, _ in md_rows if no == 0)
        new_lines = [format_table_row(sheet_by_id[tc_id]) for tc_id in sheet_only]
        lines[first_table_last + 1 : first_table_last + 1] = new_lines

    try:
        with open(args.input, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
    except OSError as exc:
        print(f"[오류] md 파일 저장에 실패했습니다: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"\n{args.input} 에 시트 내용을 반영했습니다. Priority 산정 근거와 변경 이력은 별도로 갱신하세요.")


def print_sheet_table(sh, worksheet_name, header_row):
    """워크시트를 읽기 전용으로 조회해 Markdown 표로 출력한다(쓰기 호출 없음)."""
    try:
        ws = sh.worksheet(worksheet_name)
    except Exception:  # noqa: BLE001 - gspread.WorksheetNotFound 등
        print(f"[오류] 워크시트 '{worksheet_name}'를 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    try:
        values = ws.get_all_values()
    except Exception as exc:  # noqa: BLE001 - API 오류를 사용자에게 그대로 보고
        print(f"[오류] 워크시트 '{worksheet_name}' 조회에 실패했습니다: {exc}", file=sys.stderr)
        sys.exit(1)

    header_index = header_row - 1
    if header_index < 0 or len(values) <= header_index:
        print(
            f"[오류] 워크시트 '{worksheet_name}'에 {header_row}행(헤더)이 없습니다.",
            file=sys.stderr,
        )
        sys.exit(1)

    header = values[header_index]
    data_rows = [row for row in values[header_index + 1 :] if any(cell.strip() for cell in row)]

    print(f"워크시트: {worksheet_name} (헤더 {header_row}행, 총 {len(data_rows)}건)")
    print("| " + " | ".join(header) + " |")
    print("|" + "|".join(["---"] * len(header)) + "|")
    for row in data_rows:
        padded = row + [""] * (len(header) - len(row))
        print("| " + " | ".join(padded[: len(header)]) + " |")


def cmd_risk_list(args):
    """Feature Risk Matrix를 읽기 전용으로 조회한다(쓰기 호출 없음)."""
    _, sh = get_client_and_sheet(sheet_id_env="GOOGLE_RISK_SHEET_ID")
    worksheet_name = args.worksheet or os.environ.get("GOOGLE_RISK_WORKSHEET", DEFAULT_RISK_WORKSHEET_NAME)
    print_sheet_table(sh, worksheet_name, args.header_row)


def cmd_sheet_tabs(args):
    """Risk 스프레드시트(GOOGLE_RISK_SHEET_ID)의 탭 이름 목록을 읽기 전용으로 출력한다."""
    _, sh = get_client_and_sheet(sheet_id_env="GOOGLE_RISK_SHEET_ID")
    try:
        names = [ws.title for ws in sh.worksheets()]
    except Exception as exc:  # noqa: BLE001 - API 오류를 사용자에게 그대로 보고
        print(f"[오류] 탭 목록 조회에 실패했습니다: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"탭 {len(names)}개:")
    for name in names:
        print(f"- {name}")


def cmd_sheet_read(args):
    """Risk 스프레드시트(GOOGLE_RISK_SHEET_ID)의 임의 탭을 읽기 전용으로 조회한다."""
    _, sh = get_client_and_sheet(sheet_id_env="GOOGLE_RISK_SHEET_ID")
    print_sheet_table(sh, args.worksheet, args.header_row)


def collect_regression_rows(sh, source_names):
    """전체 TC 워크시트들에서 'Regression 여부'를 읽어 (선택된 TC 행, 값 오류 목록)을 반환한다.

    읽기 전용이다. 값은 공백 제거·대소문자 무시로 비교하며, "O"만 Regression TC로 선택한다.
    "X"는 제외하고, 그 외 값(빈 값 포함)은 오류 목록으로 모은다. 헤더나 워크시트에 문제가 있으면 중단한다.
    """
    selected = []
    invalid = []
    for name in source_names:
        ws, _, _ = get_or_create_worksheet(sh, create_if_missing=False, worksheet_name=name)
        if ws is None:
            print(f"[오류] 원본 워크시트 '{name}'를 찾을 수 없습니다.", file=sys.stderr)
            sys.exit(1)
        values = ws.get_all_values()
        if not values or values[0] != SHEET_TC_COLUMNS:
            print(
                f"[오류] 원본 워크시트 '{name}'의 헤더가 TC 컬럼 정의('{REGRESSION_COLUMN}' 열 포함 11개)와 다릅니다.",
                file=sys.stderr,
            )
            print(f"  기존 헤더: {values[0] if values else []}", file=sys.stderr)
            sys.exit(1)

        header = values[0]
        id_index = header.index("ID")
        mark_index = header.index(REGRESSION_COLUMN)
        for row_no, row in enumerate(values[1:], start=2):
            padded = row + [""] * (len(header) - len(row))
            if not any(cell.strip() for cell in padded):
                continue
            tc_id = padded[id_index].strip()
            mark = padded[mark_index].strip().upper()
            if tc_id and mark == "O":
                selected.append(dict(zip(TC_COLUMNS, padded[: len(TC_COLUMNS)])))
            elif tc_id and mark == "X":
                continue
            else:
                invalid.append(f"{name}!{row_no} {tc_id or '(ID 없음)'}: '{padded[mark_index].strip()}'")
    return selected, invalid


def validate_regression_selection(selected, invalid):
    """값 오류, O 0건, ID 중복이 있으면 원인을 출력하고 중단한다."""
    if invalid:
        print(
            f"[오류] '{REGRESSION_COLUMN}' 값이 O/X가 아니거나 비어 있는 행이 있습니다. "
            "사용자가 O/X를 모두 입력한 뒤 다시 실행하세요.",
            file=sys.stderr,
        )
        for item in invalid:
            print(f"  - {item}", file=sys.stderr)
        sys.exit(1)

    if not selected:
        print(f"[오류] '{REGRESSION_COLUMN}'이 O인 TC가 없습니다.", file=sys.stderr)
        sys.exit(1)

    seen = set()
    dups = set()
    for row in selected:
        if row["ID"] in seen:
            dups.add(row["ID"])
        seen.add(row["ID"])
    if dups:
        print("[오류] O로 선택된 TC 중 ID가 중복됩니다: " + ", ".join(sorted(dups)), file=sys.stderr)
        sys.exit(1)


def get_source_names(args):
    return args.source_worksheet or [os.environ.get("GOOGLE_SHEET_WORKSHEET", DEFAULT_WORKSHEET_NAME)]


def cmd_regression_list(args):
    """전체 TC 워크시트에서 'Regression 여부'가 O인 TC를 읽기 전용으로 조회한다(쓰기 호출 없음)."""
    source_names = get_source_names(args)
    _, sh = get_client_and_sheet()
    selected, invalid = collect_regression_rows(sh, source_names)
    validate_regression_selection(selected, invalid)

    if args.ids_only:
        for row in selected:
            print(row["ID"])
        return

    print(f"원본 워크시트: {', '.join(source_names)} (Regression TC {len(selected)}건)")
    print("| " + " | ".join(TC_COLUMNS) + " |")
    print("|" + "|".join(["---"] * len(TC_COLUMNS)) + "|")
    for row in selected:
        print("| " + " | ".join(row[col].replace("\n", " ") for col in TC_COLUMNS) + " |")


def cmd_regression_create(args):
    """전체 TC 워크시트에서 'Regression 여부'가 O인 TC만 모아 새 워크시트를 만든다.

    원본 워크시트에는 어떤 쓰기도 하지 않으며, 'Regression 여부' 값은 사용자가 입력한 그대로만 읽는다.
    """
    source_names = get_source_names(args)
    dest_name = args.worksheet or os.environ.get(
        "GOOGLE_SHEET_REGRESSION_WORKSHEET", DEFAULT_REGRESSION_WORKSHEET_NAME
    )
    if dest_name in source_names:
        print("[오류] 대상 워크시트가 원본 워크시트와 같습니다.", file=sys.stderr)
        sys.exit(1)

    _, sh = get_client_and_sheet()

    dest_exists = True
    try:
        sh.worksheet(dest_name)
    except Exception:  # noqa: BLE001 - gspread.WorksheetNotFound 등
        dest_exists = False
    if dest_exists:
        print(
            f"[오류] 워크시트 '{dest_name}'가 이미 존재합니다. 기존 워크시트를 덮어쓰지 않고 중단합니다.",
            file=sys.stderr,
        )
        sys.exit(1)

    selected, invalid = collect_regression_rows(sh, source_names)
    validate_regression_selection(selected, invalid)

    print(f"원본 워크시트: {', '.join(source_names)}")
    print(f"대상 워크시트: {dest_name} (신규 생성 예정)")
    print(f"Regression TC 수: {len(selected)}건")
    print("TC ID: " + ", ".join(row["ID"] for row in selected))

    if args.dry_run:
        print("\n[dry-run] 실제로 Spreadsheet에 반영하지 않았습니다.")
        return

    ws = sh.add_worksheet(title=dest_name, rows=max(1000, len(selected) + 10), cols=len(TC_COLUMNS))
    ws.append_row(TC_COLUMNS, value_input_option="USER_ENTERED")
    ws.append_rows([[row[col] for col in TC_COLUMNS] for row in selected], value_input_option="USER_ENTERED")
    print(f"\n워크시트 '{dest_name}'를 생성하고 {len(selected)}건을 추가했습니다.")


def cmd_candidate_create_worksheet(args):
    _, sh = get_client_and_sheet()
    worksheet_name = args.worksheet or os.environ.get(
        "GOOGLE_SHEET_CANDIDATE_WORKSHEET", DEFAULT_CANDIDATE_WORKSHEET_NAME
    )
    try:
        sh.worksheet(worksheet_name)
        print(
            f"[오류] 워크시트 '{worksheet_name}'가 이미 존재합니다. "
            "기존 워크시트를 그대로 사용하세요(새로 만들지 않았습니다).",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception:  # noqa: BLE001 - gspread.WorksheetNotFound 등
        pass

    ws = sh.add_worksheet(title=worksheet_name, rows=1000, cols=len(CANDIDATE_FULL_COLUMNS))
    ws.append_row(CANDIDATE_FULL_COLUMNS, value_input_option="USER_ENTERED")
    print(f"워크시트 '{worksheet_name}'를 생성했습니다. (컬럼: {', '.join(CANDIDATE_FULL_COLUMNS)})")


def cmd_candidate_sync(args):
    if not os.path.isfile(args.input):
        print(f"[오류] 입력 파일을 찾을 수 없습니다: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        markdown_text = f.read()

    new_rows = parse_candidate_ai_table(markdown_text)
    if not new_rows:
        print(
            f"[오류] {args.input} 에서 Candidate 'AI 평가 결과' 표(10개 컬럼)와 일치하는 표를 찾지 못했습니다.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 입력 파일 내 TC ID 중복 검사
    seen = {}
    dups_in_file = []
    for row in new_rows:
        tc_id = row["TC ID"]
        if tc_id in seen:
            dups_in_file.append(tc_id)
        seen[tc_id] = True
    if dups_in_file:
        print(
            "[오류] 입력 파일 내에 중복된 TC ID가 있습니다: " + ", ".join(sorted(set(dups_in_file))),
            file=sys.stderr,
        )
        sys.exit(1)

    _, sh = get_client_and_sheet()
    worksheet_name = args.worksheet or os.environ.get(
        "GOOGLE_SHEET_CANDIDATE_WORKSHEET", DEFAULT_CANDIDATE_WORKSHEET_NAME
    )
    ws, worksheet_name, _created = get_or_create_worksheet(
        sh,
        create_if_missing=False,
        worksheet_name=worksheet_name,
        columns=CANDIDATE_FULL_COLUMNS,
        default_name=DEFAULT_CANDIDATE_WORKSHEET_NAME,
    )
    if ws is None:
        print(
            f"[오류] 워크시트 '{worksheet_name}'가 아직 없습니다. "
            "먼저 'candidate-create-worksheet'로 생성하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    values = ws.get_all_values()
    if not values:
        print(
            f"[오류] 워크시트 '{worksheet_name}'에 헤더가 없습니다. "
            "먼저 'candidate-create-worksheet'로 올바르게 생성하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    header = values[0]
    if header != CANDIDATE_FULL_COLUMNS:
        print(
            "[오류] 기존 워크시트의 헤더가 Candidate 컬럼 정의와 다릅니다. "
            "시트를 임의로 덮어쓰지 않고 중단합니다.",
            file=sys.stderr,
        )
        print(f"  기존 헤더: {header}", file=sys.stderr)
        print(f"  기대 헤더: {CANDIDATE_FULL_COLUMNS}", file=sys.stderr)
        sys.exit(1)

    id_col_index = header.index("TC ID")
    existing_row_of_id = {}
    for row_idx, row in enumerate(values[1:], start=2):  # 1행은 헤더, 데이터는 2행부터
        if len(row) > id_col_index and row[id_col_index].strip():
            existing_row_of_id[row[id_col_index].strip()] = row_idx

    rows_to_append = [row for row in new_rows if row["TC ID"] not in existing_row_of_id]
    rows_to_update = [row for row in new_rows if row["TC ID"] in existing_row_of_id]

    print(f"입력 파일: {args.input}")
    print(f"대상 워크시트: {worksheet_name}")
    print(f"신규 추가될 TC: {len(rows_to_append)}건" + (f" ({', '.join(r['TC ID'] for r in rows_to_append)})" if rows_to_append else ""))
    print(f"AI 영역만 갱신될 기존 TC: {len(rows_to_update)}건" + (f" ({', '.join(r['TC ID'] for r in rows_to_update)})" if rows_to_update else ""))
    print("(QA Decision / QA Comment는 이 명령으로 변경되지 않습니다.)")

    if args.dry_run:
        print("\n[dry-run] 실제로 Spreadsheet에 반영하지 않았습니다.")
        return

    last_ai_col_letter = column_letter(len(CANDIDATE_AI_COLUMNS))
    for row in rows_to_update:
        row_idx = existing_row_of_id[row["TC ID"]]
        values_for_row = [row[col] for col in CANDIDATE_AI_COLUMNS]
        ws.update(
            range_name=f"A{row_idx}:{last_ai_col_letter}{row_idx}",
            values=[values_for_row],
        )

    if rows_to_append:
        rows_payload = [
            [row[col] for col in CANDIDATE_AI_COLUMNS] + ["", ""] for row in rows_to_append
        ]
        ws.append_rows(rows_payload, value_input_option="USER_ENTERED")

    print(
        f"\n완료: 신규 {len(rows_to_append)}건 추가, 기존 {len(rows_to_update)}건 AI 영역 갱신 "
        f"(워크시트 '{worksheet_name}')."
    )


def cmd_candidate_list(args):
    _, sh = get_client_and_sheet()
    worksheet_name = args.worksheet or os.environ.get(
        "GOOGLE_SHEET_CANDIDATE_WORKSHEET", DEFAULT_CANDIDATE_WORKSHEET_NAME
    )
    ws, worksheet_name, _created = get_or_create_worksheet(
        sh,
        create_if_missing=False,
        worksheet_name=worksheet_name,
        columns=CANDIDATE_FULL_COLUMNS,
        default_name=DEFAULT_CANDIDATE_WORKSHEET_NAME,
    )

    if ws is None:
        print(f"워크시트 '{worksheet_name}'가 아직 없습니다. 평가된 TC가 없습니다.")
        return

    values = ws.get_all_values()
    if not values:
        print(f"워크시트 '{worksheet_name}'에 데이터가 없습니다.")
        return

    header = values[0]
    data_rows = values[1:]

    print(f"워크시트: {worksheet_name} (총 {len(data_rows)}건)")
    print("| " + " | ".join(header) + " |")
    print("|" + "|".join(["---"] * len(header)) + "|")
    for row in data_rows:
        padded = row + [""] * (len(header) - len(row))
        print("| " + " | ".join(padded[: len(header)]) + " |")


def main():
    parser = argparse.ArgumentParser(description="TC Markdown 문서를 Google Spreadsheet에 동기화한다.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="Spreadsheet의 기존 TC 목록을 조회한다.")
    list_parser.add_argument(
        "--ids-only", action="store_true", help="TC ID만 한 줄에 하나씩 출력한다."
    )
    list_parser.add_argument(
        "--worksheet", default=None, help="대상 워크시트(탭) 이름 (기본값: GOOGLE_SHEET_WORKSHEET 환경변수 또는 'TC')"
    )
    list_parser.add_argument(
        "--feature", default=None, help="Feature slug (예: search -> 'Testcase_Search' 시트 조회). --worksheet가 우선"
    )
    list_parser.set_defaults(func=cmd_list)

    append_parser = subparsers.add_parser("append", help="Markdown TC 문서를 Spreadsheet에 추가한다.")
    append_parser.add_argument("--input", required=True, help="docs/tc/{feature-slug}.md 경로")
    append_parser.add_argument(
        "--dry-run", action="store_true", help="실제로 반영하지 않고 미리보기만 출력한다."
    )
    append_parser.add_argument(
        "--worksheet", default=None, help="대상 워크시트(탭) 이름 (기본값: 입력 파일명 기준 Feature 시트, 예: search.md -> 'Testcase_Search')"
    )
    append_parser.set_defaults(func=cmd_append)

    candidate_create_parser = subparsers.add_parser(
        "candidate-create-worksheet", help="자동화 후보 평가용 워크시트를 생성한다(이미 있으면 오류)."
    )
    candidate_create_parser.add_argument(
        "--worksheet",
        default=None,
        help=f"대상 워크시트(탭) 이름 (기본값: GOOGLE_SHEET_CANDIDATE_WORKSHEET 환경변수 또는 '{DEFAULT_CANDIDATE_WORKSHEET_NAME}')",
    )
    candidate_create_parser.set_defaults(func=cmd_candidate_create_worksheet)

    candidate_sync_parser = subparsers.add_parser(
        "candidate-sync",
        help="Candidate 문서의 AI 작성 영역을 Spreadsheet에 반영한다(QA Decision/QA Comment는 보존).",
    )
    candidate_sync_parser.add_argument(
        "--input", required=True, help="docs/tc/automation-candidates/{feature-slug}.md 경로"
    )
    candidate_sync_parser.add_argument(
        "--dry-run", action="store_true", help="실제로 반영하지 않고 미리보기만 출력한다."
    )
    candidate_sync_parser.add_argument(
        "--worksheet",
        default=None,
        help=f"대상 워크시트(탭) 이름 (기본값: GOOGLE_SHEET_CANDIDATE_WORKSHEET 환경변수 또는 '{DEFAULT_CANDIDATE_WORKSHEET_NAME}')",
    )
    candidate_sync_parser.set_defaults(func=cmd_candidate_sync)

    candidate_list_parser = subparsers.add_parser(
        "candidate-list", help="자동화 후보 워크시트를 조회한다(QA Decision/QA Comment 포함)."
    )
    candidate_list_parser.add_argument(
        "--worksheet",
        default=None,
        help=f"대상 워크시트(탭) 이름 (기본값: GOOGLE_SHEET_CANDIDATE_WORKSHEET 환경변수 또는 '{DEFAULT_CANDIDATE_WORKSHEET_NAME}')",
    )
    candidate_list_parser.set_defaults(func=cmd_candidate_list)

    risk_list_parser = subparsers.add_parser(
        "risk-list", help="Feature Risk Matrix를 읽기 전용으로 조회한다(별도 스프레드시트: GOOGLE_RISK_SHEET_ID)."
    )
    risk_list_parser.add_argument(
        "--worksheet",
        default=None,
        help=f"대상 워크시트(탭) 이름 (기본값: GOOGLE_RISK_WORKSHEET 환경변수 또는 '{DEFAULT_RISK_WORKSHEET_NAME}')",
    )
    risk_list_parser.add_argument(
        "--header-row",
        type=int,
        default=DEFAULT_RISK_HEADER_ROW,
        help=f"헤더가 있는 행 번호 (기본값: {DEFAULT_RISK_HEADER_ROW})",
    )
    risk_list_parser.set_defaults(func=cmd_risk_list)

    pull_parser = subparsers.add_parser(
        "pull",
        help="시트의 TC를 읽어 Markdown TC 문서에 반영한다(시트→md, 시트는 수정하지 않음).",
    )
    pull_parser.add_argument("--input", required=True, help="docs/tc/{feature-slug}.md 경로")
    pull_parser.add_argument(
        "--dry-run", action="store_true", help="md를 수정하지 않고 차이만 출력한다."
    )
    pull_parser.add_argument(
        "--worksheet", default=None, help="대상 워크시트(탭) 이름 (기본값: 입력 파일명 기준 Feature 시트, 예: search.md -> 'Testcase_Search')"
    )
    pull_parser.set_defaults(func=cmd_pull)

    sheet_tabs_parser = subparsers.add_parser(
        "sheet-tabs", help="Risk 스프레드시트(GOOGLE_RISK_SHEET_ID)의 탭 이름 목록을 읽기 전용으로 조회한다."
    )
    sheet_tabs_parser.set_defaults(func=cmd_sheet_tabs)

    sheet_read_parser = subparsers.add_parser(
        "sheet-read",
        help="Risk 스프레드시트(GOOGLE_RISK_SHEET_ID)의 지정한 탭을 읽기 전용으로 조회한다(QA plan 등 참고자료용).",
    )
    sheet_read_parser.add_argument("--worksheet", required=True, help="조회할 워크시트(탭) 이름")
    sheet_read_parser.add_argument(
        "--header-row", type=int, default=1, help="헤더가 있는 행 번호 (기본값: 1)"
    )
    sheet_read_parser.set_defaults(func=cmd_sheet_read)

    regression_list_parser = subparsers.add_parser(
        "regression-list",
        help=f"전체 TC 워크시트에서 '{REGRESSION_COLUMN}'이 O인 TC를 읽기 전용으로 조회한다.",
    )
    regression_list_parser.add_argument(
        "--source-worksheet",
        nargs="+",
        default=None,
        help="원본 전체 TC 워크시트 이름(여러 개 가능, 기본값: GOOGLE_SHEET_WORKSHEET 환경변수 또는 'TC')",
    )
    regression_list_parser.add_argument(
        "--ids-only", action="store_true", help="TC ID만 한 줄에 하나씩 출력한다."
    )
    regression_list_parser.set_defaults(func=cmd_regression_list)

    regression_parser = subparsers.add_parser(
        "regression-create",
        help=f"'{REGRESSION_COLUMN}'이 O인 TC만 모아 새 Regression 워크시트를 생성한다(원본 시트는 수정하지 않음).",
    )
    regression_parser.add_argument(
        "--source-worksheet",
        nargs="+",
        default=None,
        help="원본 전체 TC 워크시트 이름(여러 개 가능, 기본값: GOOGLE_SHEET_WORKSHEET 환경변수 또는 'TC')",
    )
    regression_parser.add_argument(
        "--worksheet",
        default=None,
        help=(
            "생성할 Regression 워크시트 이름 "
            f"(기본값: GOOGLE_SHEET_REGRESSION_WORKSHEET 환경변수 또는 '{DEFAULT_REGRESSION_WORKSHEET_NAME}')"
        ),
    )
    regression_parser.add_argument(
        "--dry-run", action="store_true", help="실제로 반영하지 않고 미리보기만 출력한다."
    )
    regression_parser.set_defaults(func=cmd_regression_create)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
