# MTA Passenger Station Power Limits Pipeline

This repository converts semi-structured MTA passenger station power limit text files into CSV outputs that are usable for analysis and downstream reporting.

## Overview

This pipeline is split into three stages so the raw text parsing stays separate from the later grouping logic:

1. `parse_into_csv.py` extracts raw station records from text files into a normalized intermediate CSV format.
2. `group_zone.py` resolves zone-level metadata such as print codes and line names, then expands the intermediate data into station-level grouped output.
3. `per_track.py` reuses the same zone resolution logic and produces the final per-track dataset with substation and CBH context attached.

The source files are not consistently formatted, so the scripts deliberately preserve a number of case-specific rules instead of trying to aggressively normalize everything upfront.

## What The Scripts Do

`parse_into_csv.py`

- Walks the raw division folders (`BMT`, `IRT`, `IND`)
- Parses case-specific records from `.txt` files
- Extracts rows into `data_extracted/intial_processed/<DIVISION>.csv`
- Logs unmatched lines to `data_extracted/intial_processed/unable_to_process.csv`
- Logs non-text files to `data_extracted/intial_processed/unprocessed_files.csv`

Recognized cases in the raw text:

- `zone` and the OCR edge case `z0ne`
- `track ...`
- `tk. ...`
- `substation` sections
- `circuit breaker house` sections
- short standalone print codes like `201-52,70`, which are treated as incomplete files

`group_zone.py`

- Reads the initial processed division CSVs
- Resolves the zone, print code(s), and line/train text for each stop
- Expands multi-zone records into one row per zone
- Produces a grouped station-level file at `data_extracted/grouped_processed/Passenger Station Power Limits.csv`
- Logs zone parsing failures to `data_extracted/grouped_processed/group_zone_unable_to_process.csv`

`per_track.py`

- Reads the same initial processed division CSVs
- Reuses the zone parsing logic from `group_zone.py`
- Produces one row per track or incomplete entry
- Carries substation and CBH names alongside each track row
- Falls back to a zone-only row when a file has no track rows
- Writes `data_extracted/grouped_processed/Passenger Station Power Limits V.2.csv`
- Logs failures to `data_extracted/grouped_processed/per_track_unable_to_process.csv`

## Expected Layout

The scripts expect the raw source folders at the repo root:

```text
PASSENGER-POWER-LIMITS/
├── BMT/
├── IND/
├── IRT/
├── parse_into_csv.py
├── group_zone.py
└── per_track.py
```

Generated files are written under:

```text
data_extracted/
├── intial_processed/
└── grouped_processed/
```

Note: the directory name is intentionally spelled `intial_processed` because that name is already used throughout the code and output paths.

## Run Order

Run the scripts in this order:

```bash
python3 parse_into_csv.py
python3 group_zone.py
python3 per_track.py
```

## Parsing Notes

The parser is intentionally conservative because the source files contain real formatting exceptions.

- Track descriptions may span multiple lines; the parser keeps reading until it sees the expected blank-line boundary.
- Zone descriptions may use either `-` or `=` between the print prefix and the number list.
- Some files contain only an incomplete print code with no usable zone line; those records are preserved instead of being dropped.
- Duplicate folders are skipped when the path contains `dup`.

## Function Notes

The code is organized around a small number of parsing helpers with very specific responsibilities:

- `parse_section_items(...)` reads substation and CBH sections while tolerating extra blank lines inside a section.
- `get_full_track_line(...)` continues reading until a multiline track description is complete.
- `parse_name_desc(...)` handles the different ways zone and track identifiers appear in the raw text.
- `handle_zone(...)` is the shared zone-resolution function used by both grouped outputs, including incomplete-file handling.
- `get_track_rows(...)` in `per_track.py` preserves the fallback behavior for files that contain zone information but no track rows.

## Example

Raw text:

```text
Zone - 33     201 - 118     Fulton Line

TK.A1 - Atlantic Ave s/s gap - Elton s/s gap
TK.A2 - Elton s/s gap - Atlantic Ave s/s gap
```

Track-level output shape:

```csv
Division,Stop Name,Print,Line & Trains,Track Name,Limits,Zone,CBH,Substation,Is File Complete
IND,Atlantic Ave,201-118,FULTON LINE,TK. A1,ATLANTIC AVE S/S GAP - ELTON S/S GAP,ZONE 33,,,TRUE
IND,Atlantic Ave,201-118,FULTON LINE,TK. A2,ELTON S/S GAP - ATLANTIC AVE S/S GAP,ZONE 33,,,TRUE
```

