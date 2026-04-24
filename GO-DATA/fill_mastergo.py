def get_headers(ws):
    return {
        str(cell.value).strip().lower(): idx + 1
        for idx, cell in enumerate(ws[1])
        if cell.value
    }

def ensure_cols(ws, headers, cols):
    col_map = {}
    for col in cols:
        key = col.lower()
        if key in headers:
            col_map[col] = headers[key]
        else:
            idx = ws.max_column + 1
            ws.cell(row=1, column=idx, value=col)
            headers[key] = idx
            col_map[col] = idx
    return headers, col_map


def fill_TRONAME(ws, row, col_map):
    col = col_map["TRO Name (REQUIRED)"]
    fill_value = ""
    cell = ws.cell(row=row, column=col)

    if not cell.value or str(cell.value).strip() == "":
        cell.value = fill_value


def fill_days_empty(ws, row, col_map):
    col = col_map["Days (REQUIRED)"]
    fill_value = "SUN - SUN"
    cell = ws.cell(row=row, column=col)

    if not cell.value or str(cell.value).strip() == "":
        cell.value = fill_value


def fill_record_created_on(ws, row, col_map):
    col_to_fill = col_map["Record Created On (REQUIRED)"]
    col_to_copy = col_map["Scheduled Time (REQUIRED)"]

    target_cell = ws.cell(row=row, column=col_to_fill)
    source_cell = ws.cell(row=row, column=col_to_copy)

    if (not target_cell.value or str(target_cell.value).strip() == "") and source_cell.value:
        target_cell.value = source_cell.value


def fill_duration_printed_as(ws, row, col_map):
    col = col_map["Duration Printed As (REQUIRED)"]
    fill_value = "No Text"
    cell = ws.cell(row=row, column=col)

    if not cell.value or str(cell.value).strip() == "":
        cell.value = fill_value


def clean_line_access_database(ws, row, col_map):
    target_col = col_map["LINE (ACCESS DATABASE)"]

    line_cols = [
        "Line 1", "Line 2", "Line 3",
        "Line 4", "Line 5", "Line 6"
    ]

    values = []
    for col_name in line_cols:
        if col_name in col_map:
            val = ws.cell(row=row, column=col_map[col_name]).value
            if val and str(val).strip():
                values.append(str(val).strip())

    new_line = "/".join(values)

    ws.cell(row=row, column=target_col).value = new_line

def fill_division(ws, row, col_map):
    target_col = col_map["Division (REQUIRED)"]
    fill_col = col_map["Desk (REQUIRED)"]

    source_cell = ws.cell(row=row, column=fill_col)
    val = source_cell.value

    if val and str(val).strip():
        cleaned = str(val).strip().upper()
        division = cleaned[:3]  # first three characters
        ws.cell(row=row, column=target_col).value = division

def clean_text(ws, row, target_col):
    cell = ws.cell(row=row, column=target_col)
    val = cell.value

    if not val:
        return

    # Split into lines
    lines = str(val).splitlines()

    # Clean each line: strip + remove extra spaces
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped:  # skip empty lines
            normalized = " ".join(stripped.split())
            cleaned_lines.append(normalized)

    # Join into one line (or change to '\n'.join(...) if you want multiline cleaned)
    final_value = " ".join(cleaned_lines)

    cell.value = final_value

def process(ws):
    headers = get_headers(ws)

    required_cols = [
        "TRO Name (REQUIRED)",
        "Days (REQUIRED)",
        "Record Created On (REQUIRED)",
        "Scheduled Time (REQUIRED)",
        "Duration Printed As (REQUIRED)",
        "LINE (ACCESS DATABASE)",
        "Line 1", "Line 2", "Line 3",
        "Line 4", "Line 5", "Line 6",
        "Division (REQUIRED)",
        "Desk (REQUIRED)", 
        "Limits", 
        "Notes"
    ]

    headers, col_map = ensure_cols(ws, headers, required_cols)

    for row in range(2, ws.max_row + 1):
        fill_TRONAME(ws, row, col_map)
        fill_days_empty(ws, row, col_map)
        fill_record_created_on(ws, row, col_map)
        fill_duration_printed_as(ws, row, col_map)
        clean_line_access_database(ws, row, col_map)
        fill_division(ws, row, col_map)
        clean_text(ws, row, col_map["Limits"])
        clean_text(ws, row, col_map["Notes"])