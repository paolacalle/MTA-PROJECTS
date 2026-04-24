import pandas as pd
import sys
import os

import re

def make_safe_filename(name, max_len=50):
    # Replace invalid characters with underscore
    name = re.sub(r'[\\/*?:"<>|#()]', '_', str(name))
    
    # Collapse multiple underscores
    name = re.sub(r'_+', '_', name)
    
    # Trim length to avoid Windows path limit
    return name[:max_len].strip('_')

def extract_unique_per_column(input_path, output_dir):
    df = pd.read_excel(input_path)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for col in df.columns:
        try:
            unique_values = df[col].dropna().unique()
            unique_df = pd.DataFrame(unique_values, columns=[col])

            safe_col_name = make_safe_filename(col)
            output_file = os.path.join(output_dir, f"{safe_col_name}.xlsx")

            unique_df.to_excel(output_file, index=False)
            print(f"Saved: {output_file}")

        except Exception as e:
            print(f"Failed for column '{col}': {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_excel_path> [output_directory]")
        sys.exit(1)

    input_path = sys.argv[1]

    # Optional output directory
    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]
    else:
        base = os.path.splitext(os.path.basename(input_path))[0]
        output_dir = f"{base}_unique_columns"

    extract_unique_per_column(input_path, output_dir)

if __name__ == "__main__":
    main()