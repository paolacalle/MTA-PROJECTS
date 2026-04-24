import pandas as pd
from collections import defaultdict
import os

INPUT_FILES = [
    "..\\mappers\\MASTERGO\\RAW\\Line 1.xlsx",
    "..\\mappers\\MASTERGO\\RAW\\Line 2.xlsx",
    "..\\mappers\\MASTERGO\\RAW\\Line 3.xlsx",
    "..\\mappers\\MASTERGO\\RAW\\Line 4.xlsx",
    "..\\mappers\\MASTERGO\\RAW\\Line 5.xlsx",
    "..\\mappers\\MASTERGO\\RAW\\Line 6.xlsx",
]

OUTPUT_LINESUNIQUE = "..\\mappers\\lines.xlsx"


def clean_value(val):
    if pd.isna(val):
        return None

    val = str(val).strip().lower()

    if val in ("nan", "none", ""):
        return None

    return val


def process_lines():
    all_values = defaultdict(set)

    for file in INPUT_FILES:
        df = pd.read_excel(file)

        if df.empty:
            continue

        first_col = df.columns[0]

        for v in df[first_col].dropna():
            v = clean_value(v)

            if v:
                file_name = os.path.splitext(os.path.basename(file))[0]
                all_values[v].add(file_name)

    rows = [
        {
            "line": line,
            "files": ", ".join(sorted(files))
        }
        for line, files in all_values.items()
    ]

    rows.sort(key=lambda x: x["line"])

    pd.DataFrame(rows).to_excel(OUTPUT_LINESUNIQUE, index=False)

    print(f"Saved {len(rows)} unique lines to: {OUTPUT_LINESUNIQUE}")
    
if __name__ == "__main__":
    process_lines()