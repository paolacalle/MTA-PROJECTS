# MTA Passenger Station Power Limits Pipeline

This project extracts and transforms MTA passenger station power limit data from unstructured .txt files into a clean, structured CSV dataset for analysis.


# Impact

1. Automated extraction from 1,000+ unstructured text files, significantly reducing manual processing time and human error
2. Standardized inconsistent data into a structured format, improving data reliability
3. Enabled downstream use in a power monitoring dashboard, supporting the power control team with faster and more informed decision-making

## Problem

Raw data is:

- Semi-structured and inconsistent
- Mixed between station-level and track-level info
- Not usable for analytics or dashboards


## Solution

Built a Python pipeline that:

- Parses raw text files
- Extracts key fields (station, line, track, zone, limits, etc.)
- Cleans and standardizes formatting
- Outputs an analysis-ready CSV


## Features

- Text parsing with regex
- Data cleaning + normalization
- Track-level data mapping
- Validation checks


## Example Input (Raw .txt)
Note: Sample data is synthetic and does not reflect real MTA data.

Zone - 33     201 - 118     Fulton Line

```
Zone - 33     201 - 118     Fulton Line

TK.A1 - Atlantic Ave s/s gap - Elton s/s gap
TK.A2 - Elton s/s gap - Atlantic Ave s/s gap
TK.A3 - Atlantic Ave s/s gap - Elton s/s gap
TK.A4 - Elton s/s gap - Atlantic Ave s/s gap
```

## Example Input (Raw .txt)

```csv
Division,Station,Line,Track,Zone,Limits,Substation,Verified,Complete
IND,Atlantic Ave,Fulton Line,TK.A1,33,"Atlantic Ave to Elton gap",EP,TRUE,TRUE
IND,Atlantic Ave,Fulton Line,TK.A2,33,"Elton gap to Atlantic Ave",EP,TRUE,TRUE
IND,Atlantic Ave,Fulton Line,TK.A3,33,"Atlantic Ave to Elton gap",EP,TRUE,TRUE
IND,Atlantic Ave,Fulton Line,TK.A4,33,"Elton gap to Atlantic Ave",EP,TRUE,TRUE
```
