"""Fill missing MASTERGO fields and normalize selected text columns."""

from worksheet_utils import ensure_cols, get_headers


def fill_tro_name(ws, row, col_map):
    """Populate an empty TRO name with the current default placeholder."""
    col = col_map["TRO Name (REQUIRED)"]
    fill_value = ""
    cell = ws.cell(row=row, column=col)

    if not cell.value or str(cell.value).strip() == "":
        cell.value = fill_value


def fill_days_empty(ws, row, col_map):
    """Fill missing schedule-day values with the default full-week label."""
    col = col_map["Days (REQUIRED)"]
    fill_value = "SUN - SUN"
    cell = ws.cell(row=row, column=col)

    if not cell.value or str(cell.value).strip() == "":
        cell.value = fill_value


def fill_record_created_on(ws, row, col_map):
    """Copy the scheduled time into record-created-on when that field is empty."""
    col_to_fill = col_map["Record Created On (REQUIRED)"]
    col_to_copy = col_map["Scheduled Time (REQUIRED)"]

    target_cell = ws.cell(row=row, column=col_to_fill)
    source_cell = ws.cell(row=row, column=col_to_copy)

    if (not target_cell.value or str(target_cell.value).strip() == "") and source_cell.value:
        target_cell.value = source_cell.value


def fill_duration_printed_as(ws, row, col_map):
    """Fill a missing duration display label with the default text."""
    col = col_map["Duration Printed As (REQUIRED)"]
    fill_value = "No Text"
    cell = ws.cell(row=row, column=col)

    if not cell.value or str(cell.value).strip() == "":
        cell.value = fill_value


def clean_line_access_database(ws, row, col_map):
    """Rebuild the combined line field from the individual line columns."""
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
    """Derive the division code from the first three characters of Desk."""
    target_col = col_map["Division (REQUIRED)"]
    fill_col = col_map["Desk (REQUIRED)"]

    source_cell = ws.cell(row=row, column=fill_col)
    val = source_cell.value

    if val and str(val).strip():
        cleaned = str(val).strip().upper()
        division = cleaned[:3]  # first three characters
        ws.cell(row=row, column=target_col).value = division

def clean_text(ws, row, target_col):
    """Collapse multiline text into a single normalized line with clean spacing."""
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
    """Apply all fill and cleanup rules across the worksheet."""
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
        fill_tro_name(ws, row, col_map)
        fill_days_empty(ws, row, col_map)
        fill_record_created_on(ws, row, col_map)
        fill_duration_printed_as(ws, row, col_map)
        clean_line_access_database(ws, row, col_map)
        fill_division(ws, row, col_map)
        clean_text(ws, row, col_map["Limits"])
        clean_text(ws, row, col_map["Notes"])
