import csv
import os
import sys
import pandas as pd
import re
from group_zone import handle_zone, write_grouped_output, write_unable_to_process

IN_DIR = "runs/data_extracted_v2/intial_processed"
OUT_DIR = "runs/data_extracted_v2/grouped_processed"


unable_to_process = []

out_df = {
    "Division": [],
    "Stop Name": [],
    "Print": [],
    "Line & Trains": [],
    "Track Name" : [],
    "Limits": [],
    "Zone": [],
    # "Track": [],
    "CBH" : [],
    "Substation" : [],
    "Is File Complete" : []
}


def iterate_stop_name(division):
    d_csv_path = os.path.join(IN_DIR, f"{division}.csv")
    df = pd.read_csv(d_csv_path)

    for stop_name, stop_name_group in df.groupby("stop_name"):
        try:
            for res in handle_zone(stop_name, stop_name_group):
                if not res:
                    continue

                zone, print_codes, line = res

                # assign as empty the name of incomplete
                stop_name_group.loc[stop_name_group["category"] == "incomplete", "name"] = ""

                tracks = stop_name_group.loc[
                    stop_name_group["category"].isin(["track", "incomplete"])
                ]

                size = tracks.shape[0]

                if size == 0:
                    print("No tracks within ", stop_name_group)
                    tracks = stop_name_group[stop_name_group["category"] == "zone"]
                    tracks["name"] = ""
                    tracks["description"] = ""
                    size = tracks.shape[0]


                out_df["Division"].extend([i for i in tracks['division']])
                out_df["Stop Name"].extend([stop_name] * size)
                out_df["Zone"].extend([zone] * size)
                out_df["Line & Trains"].extend([line] * size)

                out_df["Print"].extend([print_codes] * size)
                out_df["Limits"].extend([i for i in  tracks["description"]])

                out_df["Track Name"].extend([i for i in tracks["name"]])
                out_df["Is File Complete"].extend([i not in ["incomplete", "zone"] for i in tracks["category"]]) #just for debugging

                # Concatenate names for all substation rows
                sub_stations = (
                    stop_name_group
                    .loc[stop_name_group["category"] == "substation", "name"]
                    .dropna()               # avoid NaN in join; or use .fillna('')
                    .astype(str)            # ensure strings
                    .str.cat(sep=", ")       
                )

                # Concatenate names for all CBH rows
                cbh = (
                    stop_name_group
                    .loc[stop_name_group["category"] == "CBH", "name"]
                    .dropna()
                    .astype(str)
                    .str.cat(sep=", ")
                )

                out_df["Substation"].extend([sub_stations] * size)
                out_df["CBH"].extend([cbh] * size)
                

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
    unable_path = os.path.join(OUT_DIR, "per_track_unable_to_process.csv")
    if os.path.exists(unable_path):
        os.remove(unable_path)

    for division in runs:
        print(f"Processing {division}...")
        iterate_stop_name(division)

    write_grouped_output(out_df, "Passenger Station Power Limits V.2", OUT_DIR)
    write_unable_to_process(OUT_DIR)
