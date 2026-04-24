"""Shared worksheet utilities for header lookup and column creation."""


def get_headers(ws):
    """Return a lowercase header-to-column-index mapping for a worksheet."""
    return {
        str(cell.value).strip().lower(): idx + 1
        for idx, cell in enumerate(ws[1])
        if cell.value
    }


def ensure_cols(ws, headers, cols):
    """Ensure the requested columns exist and return their column indexes."""
    col_map = {}
    for col in cols:
        key = col.lower()
        if key in headers:
            col_map[col] = headers[key]
            continue

        idx = ws.max_column + 1
        ws.cell(row=1, column=idx, value=col)
        headers[key] = idx
        col_map[col] = idx

    return headers, col_map
