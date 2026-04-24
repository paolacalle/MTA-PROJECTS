"""Enrich the equipment log with a flag showing whether a GO exists in MASTERGO."""

import fill_exists_in_MGO as inMGO 
from workbook_runner import run_single_sheet

INPUT_EQUIPMENTLOG = r'..\EQUIPMENT LOG TABLE.xlsx'
OUTPUT_FILE = r'..\clean\EQUIPMENT\EQUIPMENT_LOG_ENRINCHED.xlsx'


def enrich_equipment_log(ws):
    """Populate the existence flag for the equipment log worksheet."""
    inMGO.process(ws=ws, target_col="Exists in MGO", go_num_col="GO # (REQUIRED)")


def main():
    """Populate the existence flag and save the enriched equipment workbook."""
    run_single_sheet(INPUT_EQUIPMENTLOG, OUTPUT_FILE, enrich_equipment_log)

if __name__ == "__main__":
    main()
