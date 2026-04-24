import json

INPUT_GONUMBERSTODATA = r'..\mappers\MASTERGO\MAPPED\gonumber_to_data.json'

with open(INPUT_GONUMBERSTODATA, "r", encoding="utf-8") as f:
    GONUMBERS = json.load(f)


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


def fill_column(ws, row, target_col, go_num_col):
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
    headers = get_headers(ws)

    required_cols = [target_col, go_num_col]

    headers, col_map = ensure_cols(ws, headers, required_cols)

    target_idx = col_map[target_col]
    go_idx = col_map[go_num_col]

    for row in range(2, ws.max_row + 1):
        fill_column(ws, row, target_idx, go_idx)