import csv
import os
import re

import pandas as pd
from pandas.api.types import is_string_dtype

IN_DIR = "data_extracted/intial_processed"
OUT_DIR = "data_extracted/grouped_processed"
DIVISIONS = ("BMT", "IRT", "IND")
UNABLE_HEADERS = ["division", "stop_name", "zone_name", "zone_desc", "reason"]

RE_PRINTCODE = re.compile(r"(\d{3})\s*-\s*(\d{1,3}(?:\s*,\s*\d{1,3})*)\s+(.*)")
RE_EPRINTCODE = re.compile(r"(\d{3})\s*=\s*(\d{1,3}(?:\s*,\s*\d{1,3})*)\s+(.*)")
RE_PRINTCODEONLY = re.compile(r"(\d{3})\s*-\s*(\d{1,3}(?:\s*,\s*\d{1,3})*)")


def empty_grouped_output():
    """
    Return the column layout for the station-level grouped output file.
    """
    return {
        "Division": [],
        "Stop Name": [],
        "Zone": [],
        "Line & Trains": [],
        "Print": [],
        "Limits": [],
        "Type": [],
        "Type Identifier": [],
    }


def parse_zone_description(zone_desc):
    """
    Extract print code(s) and line text from a zone description.

    The raw files contain multiple valid separator formats, so the function
    tries the supported regex patterns in priority order.
    """
    for pattern in (RE_PRINTCODE, RE_EPRINTCODE, RE_PRINTCODEONLY):
        match = pattern.match(zone_desc)
        if not match:
            continue

        groups = match.groups()
        if len(groups) == 3:
            prefix, nums, line = groups
        else:
            prefix, nums = groups
            line = None

        num_list = [num.strip() for num in nums.split(",")]
        print_codes = ",".join(f"{prefix}-{num}" for num in num_list)
        return print_codes, line

    return None, None


def normalize_zone_names(zone_name):
    """
    Expand a raw zone identifier string into normalized zone labels.

    Some files store multiple zones in one field or omit the literal `zone`
    prefix on part of the value, so this helper normalizes those cases before
    rows are emitted downstream.
    """
    normalized_zones = []
    for zone in zone_name.split(","):
        cleaned = zone.strip()
        if "zone" in cleaned:
            normalized_zones.append(cleaned)
        else:
            normalized_zones.append("zone " + cleaned.replace(".", ""))
    return normalized_zones


def handle_zone(stop_name, stop_name_group, unable_to_process=None):
    """
    Resolve the zone metadata for a stop and yield normalized tuples.

    Output tuples are:
    `(zone_name, print_codes, line_name)`

    This helper is shared by both output scripts so the special handling for
    missing zones and incomplete files stays consistent.
    """
    if unable_to_process is None:
        unable_to_process = []

    zone_rows = stop_name_group[stop_name_group["category"] == "zone"]
    division = (
        stop_name_group["division"].iloc[0]
        if "division" in stop_name_group.columns and not stop_name_group.empty
        else None
    )

    if zone_rows.empty:
        incomplete = stop_name_group[stop_name_group["category"] == "incomplete"]
        if not incomplete.empty:
            print_code = str(incomplete.iloc[0]["name"]).strip()
            yield None, print_code, None
            return

        unable_to_process.append(
            {
                "division": division,
                "stop_name": stop_name,
                "zone_name": None,
                "zone_desc": None,
                "reason": "no_zone_found",
            }
        )
        return

    zone_row = zone_rows.iloc[0]
    zone_name = str(zone_row["name"]).strip().replace("-", "")
    zone_desc = str(zone_row["description"]).strip()

    print_codes, line = parse_zone_description(zone_desc)
    if print_codes is None:
        unable_to_process.append(
            {
                "division": division,
                "stop_name": stop_name,
                "zone_name": zone_name,
                "zone_desc": zone_desc,
                "reason": "regex_failed",
            }
        )
        return

    for zone in normalize_zone_names(zone_name):
        yield zone, print_codes, line


def write_unable_to_process(unable_to_process, output_dir, file_name="group_zone_unable_to_process.csv"):
    """
    Write zone-resolution failures for later review.
    """
    if not unable_to_process:
        return

    out_path = os.path.join(output_dir, file_name)
    file_exists = os.path.exists(out_path)

    with open(out_path, "a", newline="", encoding="utf-8") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=UNABLE_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(unable_to_process)


def clean_desc(value):
    """
    Remove a leading dash from limit descriptions after normalization.
    """
    if pd.isna(value):
        return value
    return re.sub(r"^\s*-\s*", "", str(value))


def clean_track(value):
    """
    Convert normalized `TRACK` labels back to the preferred `TK.` output form.
    """
    if pd.isna(value):
        return value
    return str(value).replace("TRACK ", "TK. ")


def write_grouped_output(out_df, output_name, output_dir):
    """
    Materialize one grouped output CSV after uppercase and display cleanup.
    """
    if not out_df["Division"]:
        return

    out_path = os.path.join(output_dir, f"{output_name}.csv")
    df_out = pd.DataFrame(out_df)
    df_out = df_out.apply(lambda series: series.str.upper() if is_string_dtype(series) else series)

    if "Limits" in df_out.columns:
        df_out["Limits"] = df_out["Limits"].apply(clean_desc)

    if "Track Name" in df_out.columns:
        df_out["Track Name"] = df_out["Track Name"].apply(clean_track)

    df_out.to_csv(out_path, index=False)


def iterate_stop_name(division, out_df, unable_to_process):
    """
    Build the station-level grouped output for one division CSV.
    """
    d_csv_path = os.path.join(IN_DIR, f"{division}.csv")
    df = pd.read_csv(d_csv_path)

    for stop_name, stop_name_group in df.groupby("stop_name"):
        try:
            for zone, print_codes, line in handle_zone(stop_name, stop_name_group, unable_to_process):
                non_zone_rows = stop_name_group[stop_name_group["category"] != "zone"]
                size = non_zone_rows.shape[0]

                out_df["Division"].extend(non_zone_rows["division"].tolist())
                out_df["Stop Name"].extend([stop_name] * size)
                out_df["Zone"].extend([zone] * size)
                out_df["Line & Trains"].extend([line] * size)
                out_df["Print"].extend([print_codes] * size)
                out_df["Limits"].extend(non_zone_rows["description"].tolist())
                out_df["Type"].extend(non_zone_rows["category"].tolist())
                out_df["Type Identifier"].extend(non_zone_rows["name"].tolist())
        except Exception as exc:
            unable_to_process.append(
                {
                    "division": division,
                    "stop_name": stop_name,
                    "zone_name": None,
                    "zone_desc": None,
                    "reason": f"exception: {exc}",
                }
            )


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)

    output_rows = empty_grouped_output()
    unable_to_process = []

    unable_path = os.path.join(OUT_DIR, "group_zone_unable_to_process.csv")
    if os.path.exists(unable_path):
        os.remove(unable_path)

    for division in DIVISIONS:
        print(f"Processing {division}...")
        iterate_stop_name(division, output_rows, unable_to_process)

    write_grouped_output(output_rows, "Passenger Station Power Limits", OUT_DIR)
    write_unable_to_process(unable_to_process, OUT_DIR)
