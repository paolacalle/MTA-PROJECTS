# GO Data

## Overview

`go-data` contains the data-cleaning and enrichment scripts used to prepare GO-related operational spreadsheets for downstream use. The current workflow is centered on Excel workbooks and adds missing fields, standardizes text, maps initials to employee details, and expands line references into normalized output columns.

The main processing flow is driven by [mastergo.py](/Users/paolacalle/Desktop/projects/mta-cleaning/go-data/mastergo.py), which loads a source workbook, applies mapping and fill logic, and writes an enriched output file.

## Problem

The source GO spreadsheets contain inconsistent and incomplete operational data. Common issues include:

- Missing required fields such as dates, duration labels, and division values
- Initials that need to be resolved into full employee names and PASS numbers
- Combined or inconsistent line values that need to be standardized into separate line columns
- Free-text fields with inconsistent spacing and formatting

These issues make the raw files harder to audit, search, and reuse in reporting or downstream systems.

## Solution

This folder provides a set of scripts that clean and enrich the raw workbook data in-place before saving a new version.

- [mastergo.py](/Users/paolacalle/Desktop/projects/mta-cleaning/go-data/mastergo.py) runs the main enrichment workflow
- [map_initials_mastergo.py](/Users/paolacalle/Desktop/projects/mta-cleaning/go-data/map_initials_mastergo.py) maps initials to employee names and PASS numbers using JSON lookup files
- [map_lines_to_mastergo.py](/Users/paolacalle/Desktop/projects/mta-cleaning/go-data/map_lines_to_mastergo.py) expands normalized line references into `Line 1` through `Line 6`
- [fill_mastergo.py](/Users/paolacalle/Desktop/projects/mta-cleaning/go-data/fill_mastergo.py) fills default values, derives required fields, and cleans text columns such as `Limits` and `Notes`
- [equipmentlog.py](/Users/paolacalle/Desktop/projects/mta-cleaning/go-data/equipmentlog.py) enriches the equipment log by checking whether GO numbers exist in MASTERGO

## Impact

Using this workflow improves the reliability and usability of GO data by:

- Reducing manual cleanup effort
- Creating a more consistent structure across workbooks
- Making required fields available for operational review
- Improving traceability by resolving initials into names and PASS numbers
- Producing cleaner line and notes data for reporting, validation, and downstream processing

## Workflow Summary

At a high level, the MASTERGO pipeline does the following:

1. Load the source workbook.
2. Resolve writer and verifier initials into names and PASS numbers.
3. Expand line data into standardized output columns.
4. Fill missing required fields with defaults or derived values.
5. Clean selected text fields.
6. Save a new enriched workbook version.

## Sample Data

NOTE: Data is not real MTA data.

### Input Sample

```text
GO # (REQUIRED): GO-10234
Written By (Initial): jd
Verified by (Initial): ms / qa
Scheduled Time (REQUIRED): 2026-04-20 22:00
Record Created On (REQUIRED):
Days (REQUIRED):
Duration Printed As (REQUIRED):
Desk (REQUIRED): IRT Operations
Division (REQUIRED):
LINE (ACCESS DATABASE): 1/2/42 st shuttle
Line 1:
Line 2:
Line 3:
Line 4:
Line 5:
Line 6:
Limits:   Northbound only
         from Times Sq   to  96 St

Notes:  flagger required
        contact RCC before start
```

### Output Sample

```text
GO # (REQUIRED): GO-10234
Written By (Initial): jd
Written By (Name): John Doe
Written By (PASS #): 123456
Verified by (Initial): ms / qa
Verified by (Name): Maria Smith
Verified by (PASS #): 987654
Scheduled Time (REQUIRED): 2026-04-20 22:00
Record Created On (REQUIRED): 2026-04-20 22:00
Days (REQUIRED): SUN - SUN
Duration Printed As (REQUIRED): No Text
Desk (REQUIRED): IRT Operations
Division (REQUIRED): IRT
LINE (ACCESS DATABASE): 1/2/42STSHUTTLE
Line 1: 1
Line 2: 2
Line 3: 42STSHUTTLE
Line 4:
Line 5:
Line 6:
Limits: Northbound only from Times Sq to 96 St
Notes: flagger required contact RCC before start
```

### Notes

- Call out which fields were missing in the input.
- Show which columns were added or derived.
- Highlight how line mappings, names, PASS numbers, or text cleanup changed the result.
