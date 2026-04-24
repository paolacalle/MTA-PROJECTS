import os

import pandas as pd

from group_zone import handle_zone, write_grouped_output, write_unable_to_process

IN_DIR = "data_extracted/intial_processed"
OUT_DIR = "data_extracted/grouped_processed"
DIVISIONS = ("BMT", "IRT", "IND")


def empty_grouped_output():
    """
    Return the column layout for the per-track output file.
    """
    return {
        "Division": [],
        "Stop Name": [],
        "Print": [],
        "Line & Trains": [],
        "Track Name": [],
        "Limits": [],
        "Zone": [],
        "CBH": [],
        "Substation": [],
        "Is File Complete": [],
    }


def join_category_names(stop_name_group, category):
    """
    Collapse all names for a category into one comma-separated display value.

    This is used for substation and CBH metadata, which stay attached to every
    emitted track row for the same stop.
    """
    return (
        stop_name_group.loc[stop_name_group["category"] == category, "name"]
        .dropna()
        .astype(str)
        .str.cat(sep=", ")
    )


def get_track_rows(stop_name_group):
    """
    Return the rows that should drive per-track output for a stop.

    Incomplete rows are kept but their name field is cleared. If a file has no
    track rows at all, the function falls back to a synthetic zone row so the
    stop is still represented in the final output.
    """
    working_group = stop_name_group.copy()
    working_group.loc[working_group["category"] == "incomplete", "name"] = ""

    track_rows = working_group.loc[working_group["category"].isin(["track", "incomplete"])].copy()
    if not track_rows.empty:
        return track_rows

    fallback_rows = working_group.loc[working_group["category"] == "zone"].copy()
    fallback_rows["name"] = ""
    fallback_rows["description"] = ""
    return fallback_rows


def iterate_stop_name(division, out_df, unable_to_process):
    """
    Build the per-track output for one division CSV.
    """
    d_csv_path = os.path.join(IN_DIR, f"{division}.csv")
    df = pd.read_csv(d_csv_path)

    for stop_name, stop_name_group in df.groupby("stop_name"):
        try:
            for zone, print_codes, line in handle_zone(stop_name, stop_name_group, unable_to_process):
                tracks = get_track_rows(stop_name_group)
                size = tracks.shape[0]

                substation_names = join_category_names(stop_name_group, "substation")
                cbh_names = join_category_names(stop_name_group, "CBH")

                out_df["Division"].extend(tracks["division"].tolist())
                out_df["Stop Name"].extend([stop_name] * size)
                out_df["Zone"].extend([zone] * size)
                out_df["Line & Trains"].extend([line] * size)
                out_df["Print"].extend([print_codes] * size)
                out_df["Limits"].extend(tracks["description"].tolist())
                out_df["Track Name"].extend(tracks["name"].tolist())
                out_df["Is File Complete"].extend(
                    [category not in ["incomplete", "zone"] for category in tracks["category"]]
                )
                out_df["Substation"].extend([substation_names] * size)
                out_df["CBH"].extend([cbh_names] * size)
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

    unable_path = os.path.join(OUT_DIR, "per_track_unable_to_process.csv")
    if os.path.exists(unable_path):
        os.remove(unable_path)

    for division in DIVISIONS:
        print(f"Processing {division}...")
        iterate_stop_name(division, output_rows, unable_to_process)

    write_grouped_output(output_rows, "Passenger Station Power Limits V.2", OUT_DIR)
    write_unable_to_process(
        unable_to_process,
        OUT_DIR,
        file_name="per_track_unable_to_process.csv",
    )
