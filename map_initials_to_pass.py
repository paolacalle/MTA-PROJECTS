import pandas as pd
import sys
import json
import os

# File paths (use raw strings for Windows paths)
INPUT_ACTIVE = r'..\All Users - Active & Inactive.xlsx'
OUTPUT_ACTIVE = r'..\mappers\MASTERGO\MAPPED\users_active_inactive_to_pass_number.json'

INPUT_INITIALS = r'..\mappers\initials_master.xlsx'
OUTPUT_NAMETOINITIALS = r'..\mappers\MASTERGO\MAPPED\name_to_initials.json'
OUTPUT_INITIALSTONAME = r'..\mappers\MASTERGO\MAPPED\initials_to_name.json'

OUTPUT_MERGEDNAME = r'..\mappers\MASTERGO\MAPPED\merged_users.json'


def excel_to_json(input_path, output_path, key_name_col, value_col):
    df = pd.read_excel(input_path)

    result = {}

    for _, row in df.iterrows():
        name = str(row.get(key_name_col, "")).strip()
        value = str(row.get(value_col, "")).strip().lower()

        # Skip incomplete rows
        if not name or not value:
            continue

        key = name.lower()

        if key not in result:
            result[key] = value
        elif not isinstance(result[key], list):
            # Convert existing value to list
            result[key] = [result[key], value]
        else:
            result[key].append(value)

    # Save JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    print(f"Saved JSON to: {output_path}")
    return result


def merge_by_name(ls_dicts):
    merged = {}

    for d, label in ls_dicts:
        for name, value in d.items():
            if name not in merged:
                merged[name] = {}

            merged[name][label] = value

    with open(OUTPUT_MERGEDNAME, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=4)

    print(f"Merged JSON saved to: {OUTPUT_MERGEDNAME}")
    return merged


def preprocess():
    user_to_pass = excel_to_json(
        INPUT_ACTIVE,
        OUTPUT_ACTIVE,
        "Name",
        "Pass#"
    )

    user_to_initials = excel_to_json(
        INPUT_INITIALS,
        OUTPUT_NAMETOINITIALS,
        "Name",
        "Initials"  # make sure this matches your Excel column exactly
    )

    initials_to_name = excel_to_json(
        INPUT_INITIALS,
        OUTPUT_INITIALSTONAME,
        "Initials",
        "Name"  # make sure this matches your Excel column exactly
    )

    merge_by_name(
        [(user_to_pass, "pass#"), (user_to_initials, "initials")]
    )


def main():
    if len(sys.argv) < 4:
        print("Usage: python script.py <input_excel_path> <key_column> <value_column> [output_json_path]")
        sys.exit(1)

    input_path = sys.argv[1]
    key_col = sys.argv[2]
    value_col = sys.argv[3]

    if len(sys.argv) >= 5:
        output_path = sys.argv[4]
    else:
        base = os.path.splitext(input_path)[0]
        output_path = f"{base}.json"

    excel_to_json(input_path, output_path, key_col, value_col)


if __name__ == "__main__":
    # Default behavior: run your preprocessing pipeline
    preprocess()

    # If you want CLI behavior instead, comment the above and uncomment below:
    # main()