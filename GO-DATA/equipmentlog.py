from openpyxl import load_workbook
import re
import fill_exists_in_MGO as inMGO 

INPUT_EQUIPMENTLOG = r'..\EQUIPMENT LOG TABLE.xlsx'
OUTPUT_FILE = r'..\clean\EQUIPMENT\EQUIPMENT_LOG_ENRINCHED.xlsx'

WB = load_workbook(INPUT_EQUIPMENTLOG)
WS = WB.active

def main():

    inMGO.process(ws=WS, target_col="Exists in MGO", go_num_col="GO # (REQUIRED)")

    # ----------------------------
    # SAVE ONLY ONCE (FINAL STEP)
    # ----------------------------
    WB.save(OUTPUT_FILE)
    print(f"Saved enriched file to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()