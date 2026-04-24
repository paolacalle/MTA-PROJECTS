"""Mark worksheet rows whose GO number exists in the MASTERGO mapping."""

import json

from worksheet_utils import ensure_cols, get_headers

INPUT_GONUMBERSTODATA = r'..\mappers\MASTERGO\MAPPED\gonumber_to_data.json'

with open(INPUT_GONUMBERSTODATA, "r", encoding="utf-8") as f:
    GONUMBERS = json.load(f)


def fill_column(ws, row, target_col, go_num_col):
    """Write `1` when the GO number exists in MASTERGO, otherwise `0`."""
    go_val = ws.cell(row=row, column=go_num_col).value

    # normalize GO number
    if go_val is None:
        go_num = ""
    else:
        go_num = str(go_val).strip()

    target_cell = ws.cell(row=row, column=target_col)

    if not GONUMBERS.get(go_num):
        # the go-number does not exist
        target_cell.value = 0
    else:
        target_cell.value = 1


def process(ws, target_col, go_num_col):
    """Populate an existence flag column for all worksheet rows."""
    headers = get_headers(ws)

    required_cols = [target_col, go_num_col]

    headers, col_map = ensure_cols(ws, headers, required_cols)

    target_idx = col_map[target_col]
    go_idx = col_map[go_num_col]

    for row in range(2, ws.max_row + 1):
        fill_column(ws, row, target_idx, go_idx)
