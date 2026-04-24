import csv
import os
import sys
import pandas as pd
import re
from pandas.api.types import is_string_dtype
IN_DIR = "data_extracted/intial_processed"
OUT_DIR = "data_extracted/grouped_processed"

# print codes
RE_PRINTCODE = re.compile(r"(\d{3})\s*-\s*(\d{1,3}(?:\s*,\s*\d{1,3})*)\s+(.*)")
RE_EPRINTCODE = re.compile(r"(\d{3})\s*=\s*(\d{1,3}(?:\s*,\s*\d{1,3})*)\s+(.*)")
RE_PRINTCODEONLY = re.compile(r"(\d{3})\s*-\s*(\d{1,3}(?:\s*,\s*\d{1,3})*)")

unable_to_process = []

out_df = {
    "Division": [],
    "Stop Name": [],
    "Zone": [],
    "Line & Trains": [],
    "Print": [],
    "Limits": [],
    "Type": [],
    "Type Identifier" : []
}

def handle_zone(stop_name, stop_name_group):
    """
    Extract zone info and parse the print code + line from the zone description.
    Returns:
        (zone_name, print_code, line) or None
    """
    
    zone_rows = stop_name_group[stop_name_group["category"] == "zone"]

    if zone_rows.empty:
        division = (
            stop_name_group["division"].iloc[0]
            if "division" in stop_name_group.columns and not stop_name_group.empty
            else None
        )

        # fill in incomplete case
        incomplete = stop_name_group[stop_name_group["category"] == "incomplete"]
        if not incomplete.empty:
            r1 = incomplete.iloc[0]
            print_code = str(r1["name"]).strip()
            yield None, print_code, None
        else:
            unable_to_process.append({
                "division": division,
                "stop_name": stop_name,
                "zone_name": None,
                "zone_desc": None,
                "reason": "no_zone_found"
            })

        return None
    
    # take first zone row
    zone_row = zone_rows.iloc[0]
    zone_name = str(zone_row["name"]).strip().replace("-", "")
    zone_desc = str(zone_row["description"]).strip()
    division = zone_row["division"] if "division" in zone_row.index else None

    # parse the zone_desc
    m = RE_PRINTCODE.match(zone_desc)
    
    if not m:
        m = RE_EPRINTCODE.match(zone_desc)

    if not m:
        m = RE_PRINTCODEONLY.match(zone_desc)

    if m:
        g = m.groups()

        if len(g) == 3:
            prefix, nums, line = m.groups()
        else:
            prefix, nums = m.groups()
            line = None

        # normalize numbers like "52,70" -> "201-52,201-70"
        num_list = [n.strip() for n in nums.split(",")]
        print_codes = ",".join([f"{prefix}-{n}" for n in num_list])
    else:
        unable_to_process.append({
            "division": division,
            "stop_name": stop_name,
            "zone_name": zone_name,
            "zone_desc": zone_desc,
            "reason": "regex_failed"
        })
            

    # handle multple zone in one
    zones = zone_name.split(",")

    # category name
    for z in zones:
        if "zone" in z:
            yield z, print_codes, line 
        else:
            yield "zone " + z.replace(".", ""), print_codes, line
    

    return None

def write_unable_to_process(output_dir, file_name="group_zone_unable_to_process.csv"):
    """
    Write all rows that could not be processed to CSV.
    """
    if not unable_to_process:
        return
    out_path = os.path.join(output_dir, file_name)
    file_exists = os.path.exists(out_path)
    fieldnames = ["division", "stop_name", "zone_name", "zone_desc", "reason"]
    with open(out_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(unable_to_process)

def write_grouped_output(out_df, division, output_dir):
    """
    Write processed grouped output to a division CSV.
    """
    if not out_df["Division"]:
        return
    
    for col in out_df.keys():
        print(col, len(out_df[col]))
    
    out_path = os.path.join(output_dir, f"{division}.csv")
    df_out = pd.DataFrame(out_df)


    df_out = df_out.apply(
        lambda s: s.str.upper() if is_string_dtype(s) else s
    )


    def clean_desc(line):
        if pd.isna(line):
            return line
        return re.sub(r'^\s*-\s*', '', str(line))
    
    df_out["Limits"] = df_out["Limits"].apply(clean_desc)

    def clean_track(line):
        if pd.isna(line):
            return line
        return line.replace("TRACK ", "TK. ")
    
    if "Track Name" in df_out.columns:
        df_out["Track Name"] = df_out["Track Name"].apply(clean_track)

    df_out.to_csv(out_path, index=False)

def iterate_stop_name(division):
    d_csv_path = os.path.join(IN_DIR, f"{division}.csv")
    df = pd.read_csv(d_csv_path)

    for stop_name, stop_name_group in df.groupby("stop_name"):
        try:
            for res in handle_zone(stop_name, stop_name_group):
                if not res:
                    continue

                zone, print_codes, line = res

                non_zone_rows = stop_name_group[stop_name_group["category"] !=  "zone"]
                size = non_zone_rows.shape[0]
                out_df["Division"].extend([i for i in non_zone_rows['division']])
                out_df["Stop Name"].extend([stop_name] * size)
                out_df["Zone"].extend([zone] * size)
                out_df["Line & Trains"].extend([line] * size)
                out_df["Print"].extend([print_codes] * size)
                out_df["Limits"].extend([i for i in  non_zone_rows["description"]])
                out_df["Type"].extend([i for i in  non_zone_rows["category"]])
                out_df["Type Identifier"].extend([i for i in non_zone_rows["name"]])


        except Exception as e:
            unable_to_process.append({
                "division": division,
                "stop_name": stop_name,
                "zone_name": None,
                "zone_desc": None,
                "reason": f"exception: {str(e)}"
            })
    

if __name__ == "__main__":
    runs = ["BMT", "IRT", "IND"]
    os.makedirs(OUT_DIR, exist_ok=True)
    # optional: remove old failure log so each run is fresh
    unable_path = os.path.join(OUT_DIR, "unable_to_process.csv")
    if os.path.exists(unable_path):
        os.remove(unable_path)
    for division in runs:
        print(f"Processing {division}...")
        iterate_stop_name(division)
    write_grouped_output(out_df, "Passenger Station Power Limits", OUT_DIR)
    write_unable_to_process(OUT_DIR)
