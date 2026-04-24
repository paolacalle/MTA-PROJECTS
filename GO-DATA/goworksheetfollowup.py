"""Enrich the GO worksheet follow-up file with a MASTERGO existence flag."""

import fill_exists_in_MGO as inMGO 
from workbook_runner import run_single_sheet

INPUT_FOLLOWUP = r'..\GO WORKSHEET FOLLOW-UP-new.xlsx'
OUTPUT_FILE = r'..\clean\FOLLOWUP\GO_WORKSHEET_FOLLOWUP_ENRINCHED.xlsx'


def enrich_followup(ws):
    """Populate the existence flag for the follow-up worksheet."""
    inMGO.process(ws=ws, target_col="Exists in MGO", go_num_col="GO # (REQUIRED)")


def main():
    """Populate the existence flag and save the enriched follow-up workbook."""
    run_single_sheet(INPUT_FOLLOWUP, OUTPUT_FILE, enrich_followup)

if __name__ == "__main__":
    main()
