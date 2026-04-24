# Script Guide

This README is a rough guide to what each script in this folder does and the order they are typically run.

## Big Picture

There are three kinds of scripts here:

- Mapping builders: generate JSON or Excel lookup files used by the enrichment scripts.
- Main workbook enrichers: open a workbook, update the active sheet, and save an enriched copy.
- Helpers and utilities: shared functions or one-off extraction tools.

Most of the workflow centers on `mastergo.py`. The other workbook scripts depend on outputs produced by the MASTERGO flow.

## Proposed Run Order

This is the rough dependency order implied by the code:

1. `map_initials_to_pass.py`
2. `get_unique_lines.py`
3. `map_lines_to_sodosline.py`
4. `mastergo.py`
5. `map_mastergo_gonumber.py`
6. `goworksheetfollowup.py`
7. `equipmentlog.py`

Why this order:

- `map_initials_to_pass.py` creates the JSON lookup files consumed by `map_initials_mastergo.py`.
- `get_unique_lines.py` prepares the consolidated line workbook used to maintain line mappings.
- `map_lines_to_sodosline.py` converts that mapping workbook into `lines_to_sodos_lines.json`, which `map_lines_to_mastergo.py` reads.
- `mastergo.py` uses both the initials mappings and the line mappings to enrich the MASTERGO workbook.
- `map_mastergo_gonumber.py` builds `gonumber_to_data.json` from the enriched MASTERGO workbook.
- `goworksheetfollowup.py` and `equipmentlog.py` use that GO-number JSON to flag whether a GO exists in MASTERGO.

## Script-by-Script

### Main Pipeline Scripts

#### `mastergo.py`

Main MASTERGO pipeline driver.

- Opens `..\clean\MASTERGO\MASTERGO_ENRICHED_V5.xlsx`
- Runs initials mapping, line expansion, and fill/cleanup steps
- Saves `..\clean\MASTERGO\MASTERGO_ENRICHED_V6.xlsx`

This is the core script for enriching the MASTERGO workbook.

#### `goworksheetfollowup.py`

Adds an `Exists in MGO` flag to the GO worksheet follow-up workbook.

- Reads `..\GO WORKSHEET FOLLOW-UP-new.xlsx`
- Uses `fill_exists_in_MGO.py`
- Saves `..\clean\FOLLOWUP\GO_WORKSHEET_FOLLOWUP_ENRINCHED.xlsx`

Run this after `map_mastergo_gonumber.py`.

#### `equipmentlog.py`

Adds an `Exists in MGO` flag to the equipment log workbook.

- Reads `..\EQUIPMENT LOG TABLE.xlsx`
- Uses `fill_exists_in_MGO.py`
- Saves `..\clean\EQUIPMENT\EQUIPMENT_LOG_ENRINCHED.xlsx`

Run this after `map_mastergo_gonumber.py`.

### Mapping / Preprocessing Scripts

#### `map_initials_to_pass.py`

Builds lookup JSON files for names, initials, and PASS numbers.

- Reads `..\All Users - Active & Inactive.xlsx`
- Reads `..\mappers\initials_master.xlsx`
- Writes:
  - `..\mappers\MASTERGO\MAPPED\users_active_inactive_to_pass_number.json`
  - `..\mappers\MASTERGO\MAPPED\name_to_initials.json`
  - `..\mappers\MASTERGO\MAPPED\initials_to_name.json`
  - `..\mappers\MASTERGO\MAPPED\merged_users.json`

This should be run before `mastergo.py` if those JSON files need to be refreshed.

#### `get_unique_lines.py`

Collects unique values from the raw `Line 1` through `Line 6` workbooks and combines them into one Excel file.

- Reads:
  - `..\mappers\MASTERGO\RAW\Line 1.xlsx`
  - `..\mappers\MASTERGO\RAW\Line 2.xlsx`
  - `..\mappers\MASTERGO\RAW\Line 3.xlsx`
  - `..\mappers\MASTERGO\RAW\Line 4.xlsx`
  - `..\mappers\MASTERGO\RAW\Line 5.xlsx`
  - `..\mappers\MASTERGO\RAW\Line 6.xlsx`
- Writes `..\mappers\lines.xlsx`

This is useful when rebuilding or reviewing the line mapping source file.

#### `map_lines_to_sodosline.py`

Builds the JSON line mapping used by the MASTERGO enrichment pipeline.

- Reads `..\mappers\lines_master.xlsx`
- Writes `..\mappers\MASTERGO\MAPPED\lines_to_sodos_lines.json`

Run this before `mastergo.py` whenever line mappings change.

#### `map_mastergo_gonumber.py`

Builds a GO-number-to-data JSON file from the enriched MASTERGO workbook.

- Reads `..\clean\MASTERGO\MASTERGO_ENRICHED_V6.xlsx`
- Writes `..\mappers\MASTERGO\MAPPED\gonumber_to_data.json`

Run this after `mastergo.py` and before the follow-up/equipment scripts.

### Transformation Modules Used by `mastergo.py`

#### `map_initials_mastergo.py`

Maps:

- `Written By (Initial)` -> name and PASS number
- `Verified by (Initial)` -> name and PASS number

It creates or fills:

- `Written By (Name)`
- `Written By (PASS #)`
- `Verified by (Name)`
- `Verified by (PASS #)`

This is normally not run directly. `mastergo.py` calls it.

#### `map_lines_to_mastergo.py`

Expands `LINE (ACCESS DATABASE)` into:

- `Line 1`
- `Line 2`
- `Line 3`
- `Line 4`
- `Line 5`
- `Line 6`

It reads `..\mappers\MASTERGO\MAPPED\lines_to_sodos_lines.json` and `..\mappers\lines_master_map1.csv`.

This is normally not run directly. `mastergo.py` calls it.

#### `fill_mastergo.py`

Fills and cleans standard MASTERGO fields. Based on the current code, it:

- fills blank `TRO Name (REQUIRED)` with an empty placeholder
- fills blank `Days (REQUIRED)` with `SUN - SUN`
- copies `Scheduled Time (REQUIRED)` into `Record Created On (REQUIRED)` when missing
- fills blank `Duration Printed As (REQUIRED)` with `No Text`
- rebuilds `LINE (ACCESS DATABASE)` from the split line columns
- derives `Division (REQUIRED)` from the first three characters of `Desk (REQUIRED)`
- normalizes whitespace in `Limits`
- normalizes whitespace in `Notes`

This is normally not run directly. `mastergo.py` calls it.

#### `fill_exists_in_MGO.py`

Shared module used by `goworksheetfollowup.py` and `equipmentlog.py`.

- Reads `..\mappers\MASTERGO\MAPPED\gonumber_to_data.json`
- Writes `1` or `0` into a target column based on whether the GO number exists

Not usually run directly.

### Shared Helpers

#### `workbook_runner.py`

Small helper that:

- opens a workbook with `openpyxl`
- uses the active worksheet
- applies a transform function
- saves the output workbook

Used by `mastergo.py`, `goworksheetfollowup.py`, and `equipmentlog.py`.

#### `worksheet_utils.py`

Shared worksheet helpers for:

- reading header names
- ensuring required columns exist

Used by several worksheet-processing modules.

### One-Off Utilities

#### `extract_unique.py`

CLI utility that exports one Excel file per column, containing the unique non-null values from that column.

Usage:

```bash
python extract_unique.py <input_excel_path> [output_directory]
```

Useful for exploring raw data and building mapping inputs.

#### `exctract_unqiue.py`

Compatibility wrapper for the misspelled legacy script name. It just calls `extract_unique.py`.

## Practical Notes

- Many scripts use relative paths like `..\mappers\...` and `..\clean\...`, so they assume a specific directory layout one level above this folder.
- Several scripts overwrite or create downstream mapping files. If those files are manually curated, rerun the builders carefully.
- `mastergo.py` currently reads `MASTERGO_ENRICHED_V5.xlsx` and writes `MASTERGO_ENRICHED_V6.xlsx`, so the filenames reflect a versioned workflow rather than a single fixed output.

