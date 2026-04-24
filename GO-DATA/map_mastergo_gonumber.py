"""Build a GO-number lookup JSON from the enriched MASTERGO workbook."""

import pandas as pd
import json

OUTPUT_GONUMBERSTODATA = r'..\mappers\MASTERGO\MAPPED\gonumber_to_data.json'
INPUT_MASTERGO = r'..\clean\MASTERGO\MASTERGO_ENRICHED_V6.xlsx'


def build_go_mapping():
    """Create a GO-number-to-metadata mapping from required workbook columns."""
    df = pd.read_excel(INPUT_MASTERGO)

    required_cols = [
        "GO # (REQUIRED)",
        "Division (REQUIRED)",
        "GO Type (REQUIRED)",
        "Job # (REQUIRED)",
        "Desk (REQUIRED)",
        "S/S COVERAGE ?"
    ]

    # Ensure all required columns exist
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")

    mapping = {}

    for _, row in df.iterrows():
        go_number = row["GO # (REQUIRED)"]

        if pd.isna(go_number):
            continue

        go_number = str(go_number).strip()

        mapping[go_number] = {
            "Division (REQUIRED)": clean_val(row["Division (REQUIRED)"]),
            "GO Type (REQUIRED)": clean_val(row["GO Type (REQUIRED)"]),
            "Job # (REQUIRED)": clean_val(row["Job # (REQUIRED)"]),
            "Desk (REQUIRED)": clean_val(row["Desk (REQUIRED)"]),
            "S/S COVERAGE ?": clean_val(row["S/S COVERAGE ?"])
        }

    return mapping


def clean_val(val):
    """Normalize cell values for JSON output."""
    if pd.isna(val):
        return ""
    return str(val).strip()


def main():
    """Write the GO-number mapping file to disk."""
    mapping = build_go_mapping()

    with open(OUTPUT_GONUMBERSTODATA, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=4)

    print(f"Saved {len(mapping)} GO mappings.")


if __name__ == "__main__":
    main()
