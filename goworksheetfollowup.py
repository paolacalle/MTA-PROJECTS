from openpyxl import load_workbook
import re
import fill_exists_in_MGO as inMGO 

INPUT_FOLLOWUP = r'..\GO WORKSHEET FOLLOW-UP-new.xlsx'
OUTPUT_FILE = r'..\clean\FOLLOWUP\GO_WORKSHEET_FOLLOWUP_ENRINCHED.xlsx'

WB = load_workbook(INPUT_FOLLOWUP)
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