import json
import re

INPUT_INITIALSTONAME = r'..\mappers\MASTERGO\MAPPED\initials_to_name.json'
INPUT_NAMETOPASS = r'..\mappers\MASTERGO\MAPPED\users_active_inactive_to_pass_number.json'

DEFAULT_NAME = "BLANK"
DEFAULT_PASS = "BLANK"

INITIALS_COLS = ["Written By (Initial)", "Verified by (Initial)"]
NAME_COLS = ["Written By (Name)", "Verified by (Name)"]
PASS_COLS = ["Written By (PASS #)", "Verified by (PASS #)"]

# ----------------------------
# Helpers
# ----------------------------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_initials(val):
    if not val:
        return ""
    val = str(val).lower().strip()
    val = re.sub(r"\s+", "", val)
    if "/" in val:
        val = val.split("/")[0]
    return val


def safe_str(val):
    if val is None:
        return ""
    val = str(val).strip()
    if val.lower() in ("nan", "none", ""):
        return ""
    return val


def normalize_name(name):
    return safe_str(name).lower().strip()


def resolve_name(initials, initials_map):
    key = normalize_initials(initials)
    value = initials_map.get(key)

    if not value:
        return None

    if isinstance(value, list):
        for v in value:
            v = safe_str(v)
            if v:
                return v
        return None

    value = safe_str(value)
    return value if value else None


def resolve_pass(name, name_map):
    if not name:
        return None
    return name_map.get(normalize_name(name))


# ----------------------------
# Column helpers
# ----------------------------

def normalize_header(h):
    return str(h).strip().lower() if h else ""


def rebuild_headers(ws):
    headers = {}
    for idx, cell in enumerate(ws[1]):
        key = normalize_header(cell.value)
        if key:
            headers[key] = idx + 1
    return headers


def ensure_column(ws, headers, column_name):
    key = normalize_header(column_name)

    if key in headers:
        return headers, headers[key]

    new_col_idx = ws.max_column + 1
    ws.cell(row=1, column=new_col_idx, value=column_name)

    headers[key] = new_col_idx
    return headers, new_col_idx


# ----------------------------
# MAIN
# ----------------------------

def process(ws):
    initials_map = load_json(INPUT_INITIALSTONAME)
    name_map = load_json(INPUT_NAMETOPASS)

    initials_map = {normalize_initials(k): v for k, v in initials_map.items()}
    name_map = {normalize_name(k): v for k, v in name_map.items()}

    headers = rebuild_headers(ws)

    # store column indexes once
    col_map = {}

    # ensure all columns exist BEFORE processing
    for n, p, i in zip(NAME_COLS, PASS_COLS, INITIALS_COLS):
        headers, name_idx = ensure_column(ws, headers, n)
        headers, pass_idx = ensure_column(ws, headers, p)

        headers = rebuild_headers(ws)

        initials_idx = headers.get(normalize_header(i))
        if not initials_idx:
            raise ValueError(f"Missing column: {i}")

        col_map[i] = {
            "initials": initials_idx,
            "name": name_idx,
            "pass": pass_idx
        }

    # ----------------------------
    # PROCESS ALL ROWS ONCE
    # ----------------------------
    for row in range(2, ws.max_row + 1):

        for i in INITIALS_COLS:
            cols = col_map[i]

            initials = ws.cell(row=row, column=cols["initials"]).value

            name = resolve_name(initials, initials_map)
            if not name:
                name = DEFAULT_NAME

            pass_num = resolve_pass(name, name_map)
            if pass_num is None:
                pass_num = DEFAULT_PASS

            ws.cell(row=row, column=cols["name"], value=name)
            ws.cell(row=row, column=cols["pass"], value=pass_num)
