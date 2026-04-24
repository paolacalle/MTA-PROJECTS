"""Run the MASTERGO workbook enrichment pipeline.

This script loads the current MASTERGO workbook, applies the initials,
line-mapping, and fill/cleanup transformations, then saves a new enriched
version of the file.
"""

import map_initials_mastergo as mapinitials
import map_lines_to_mastergo as maplines
import fill_mastergo as filler
from workbook_runner import run_single_sheet

INPUT_MASTERGO = r'..\clean\MASTERGO\MASTERGO_ENRICHED_V5.xlsx'
OUTPUT_FILE = r'..\clean\MASTERGO\MASTERGO_ENRICHED_V6.xlsx'


def enrich_mastergo(ws):
    """Apply all MASTERGO enrichment steps to the active worksheet."""
    mapinitials.process(ws=ws)
    maplines.process(ws=ws)
    filler.process(ws=ws)

def main():
    """Execute the end-to-end MASTERGO enrichment workflow."""
    run_single_sheet(INPUT_MASTERGO, OUTPUT_FILE, enrich_mastergo)

if __name__ == "__main__":
    main()
