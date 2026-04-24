"""Run the MASTERGO workbook enrichment pipeline.

This script loads the current MASTERGO workbook, applies the initials,
line-mapping, and fill/cleanup transformations, then saves a new enriched
version of the file.
"""

from openpyxl import load_workbook
import re
import map_initials_mastergo as mapinitials
import map_lines_to_mastergo as maplines
import fill_mastergo as filler

INPUT_MASTERGO = r'..\clean\MASTERGO\MASTERGO_ENRICHED_V5.xlsx'
OUTPUT_FILE = r'..\clean\MASTERGO\MASTERGO_ENRICHED_V6.xlsx'

WB = load_workbook(INPUT_MASTERGO)
WS = WB.active

def main():
    """Execute the end-to-end MASTERGO enrichment workflow."""

    mapinitials.process(ws=WS)
    maplines.process(ws=WS)
    filler.process(ws=WS)

    # ----------------------------
    # SAVE ONLY ONCE (FINAL STEP)
    # ----------------------------
    WB.save(OUTPUT_FILE)
    print(f"Saved enriched file to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
