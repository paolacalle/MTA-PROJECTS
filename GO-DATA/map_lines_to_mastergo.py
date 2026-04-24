"""Expand combined MASTERGO line values into standardized line columns."""

import json
import pandas as pd

from worksheet_utils import ensure_cols, get_headers

INPUT_MERGEDNAME = r'..\mappers\MASTERGO\MAPPED\lines_to_sodos_lines.json'
INPUT_MAP1 = r'..\mappers\lines_master_map1.csv'

LINE_COL = "LINE (ACCESS DATABASE)"

LINE_COLS = [
    "Line 1",
    "Line 2",
    "Line 3",
    "Line 4",
    "Line 5",
    "Line 6"
]


# ----------------------------
# Helpers
# ----------------------------

def safe_str(v):
    """Return a normalized lowercase string or an empty string."""
    if v is None:
        return ""
    v = str(v).strip().lower()
    if v in ("nan", "none", ""):
        return ""
    return v


def normalize_key(v):
    """Normalize a mapping key before lookup."""
    v = safe_str(v)
    # v = re.sub(r"\s+", " ", v)
    return v


def load_json(path):
    """Load a UTF-8 JSON mapping file from disk."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ----------------------------
# Core mapping logic
# ----------------------------

def expand_maps(value, mapping, map1_unique):
    """Return the flattened mapped line list for a single input token."""
    value = normalize_key(value)

    if not value:
        return ["ERR: no match if 1 ", value]

    if value not in mapping:
        if value in map1_unique:
            return [value.upper()]
        return ["ERR: no match if 2 ", value]

    entry = mapping[value]

    maps = entry.get("maps", [])
    if isinstance(maps, str):
        maps = [maps]

    return [m.upper() for m in maps if m]


def split_input(cell_value):
    """Split a slash-delimited line field into normalized parts."""
    if not cell_value:
        return []
    return [normalize_key(x) for x in str(cell_value).split("/") if x.strip()]


# ----------------------------
# Main
# ----------------------------

def process(ws):
    """Map the combined line field into `Line 1` through `Line 6`."""
    mapping = load_json(INPUT_MERGEDNAME)
    map1_unique = [normalize_key(v) for v in pd.read_csv(INPUT_MAP1)["map1"].to_list()]

    headers = get_headers(ws)

    if LINE_COL.lower() not in headers:
        raise ValueError(f"Missing column: {LINE_COL}")

    headers, line_cols_map = ensure_cols(ws, headers, LINE_COLS)

    line_col_idx = headers[LINE_COL.lower()]

    # ----------------------------
    # Process rows
    # ----------------------------
    for row in range(2, ws.max_row + 1):

        raw_value = ws.cell(row=row, column=line_col_idx).value
        parts = split_input(raw_value)

        expanded = []
        for p in parts:
            expanded.extend(expand_maps(p, mapping, map1_unique))

        # remove duplicates but keep order
        seen = set()
        expanded = [x for x in expanded if not (x in seen or seen.add(x))]

        # write into Line 1..6
        col_idx_list = [line_cols_map[c] for c in LINE_COLS]

        i = 0
        for col_idx in col_idx_list:
            value = expanded[i] if i < len(expanded) else ""

            ws.cell(row=row, column=col_idx, value=value)
            i += 1
