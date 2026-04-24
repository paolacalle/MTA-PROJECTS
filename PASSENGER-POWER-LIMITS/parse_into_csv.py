import csv
import os
import sys
import re
 
OUT_DIR = "data_extracted/intial_processed"
unable_to_process = []
RE_PRINTCODE = re.compile(r"(\d{3})\s*-\s*(\d{1,2}(?:\s*,\s*\d{1,2})*)")
RE_TXT_FILE = re.compile(r"\.*txt", re.IGNORECASE)

def flush_queue(queue, division, output_dir):
    """
    Write queued rows to the division CSV file.
    """
    if not queue:
        return
    out_path = os.path.join(output_dir, f"{division}.csv")
    file_exists = os.path.exists(out_path)
    with open(out_path, "a", newline="", encoding="utf-8") as out_file:
        writer = csv.writer(out_file)
        if not file_exists:
            writer.writerow(["division", "stop_name", "name", "description", "category"])
        writer.writerows(queue)
    queue.clear()
 
def parse_section_items(file_obj):
    """
    Read lines after a section header until a blank line or EOF.
    Returns the non-empty lines found in that section.
    """
    items = []
    seen_count = 0
    while True:
        next_line = file_obj.readline()
        if not next_line or next_line.strip().lower() == "":
            if seen_count > 2:
                break
            seen_count += 1
            continue
        else:
            seen_count = 0
        next_line = next_line.strip().lower()
        items.append(next_line)
    return items

def get_full_track_line(file_obj, line):
    empty_count = 0
    while True:
        next_line = file_obj.readline().strip()

        if next_line == "":
            empty_count += 1
            if empty_count == 2:
                return line
            continue
        else:
            empty_count = 0
        
        if not next_line:
            raise Exception("sudden end of track")
        
        line += " " + next_line.strip().lower()

def parse_name_desc(line, line_type):
    """
    Splits and Cleans the zone and track raw line to include:
    Name and Desc.
 
    Example:
    - track g1 -bumper block n/o ditmars blvd to south washington pl. gap
 
    will be split into
    - track g1 , bumper block n/o ditmars blvd to south washington pl. gap
    """
    s = line.split(" ")
    s = [i for i in s if (i != "")]
 
    if line_type not in s[0] and line_type not in s[1]:
        raise Exception(f"expected {line_type} to be first word. Got {s[0]}. Line {line}")
   
    if "-" in s[0]:
        res = s[0].split("-", 2)

        if 1 <= len(res[1]) <= 2:
            z = res[0] + " " + res[1]

            if line_type == "zone" and "," in z:
                return z + s[1], " ".join(s[2:])

            return z, " ".join(s[1:])
        else:
            raise Exception(f"expected {line_type}-## {s[0]}", line)
 
    if s[1] == "-":
        return s[0] + " " + s[2], " ".join(s[3:])
   
    return s[0] + " " + s[1], " ".join(s[2:])
 
def parse_write(file_path, division, output_dir, queue, batch_size=1000):
    """
    Parse a single text file and add extracted rows to queue.
    """
    stop_name = os.path.splitext(os.path.basename(file_path))[0]
    with open(file_path, "r", encoding="utf-8") as file:
        s = 0
        while True:
            line = file.readline()

            if not line:
                break # EOF
 
            line = line.strip().lower()
            if line == "":
                continue

            n = len(line)
            cbh_n = len("circuit breaker house")
            sub_n = len("substation")

            if "circuit breaker house" in line:
                print(line[:cbh_n] )

            if n > 4 and line[:4] in ["zone", "z0ne"]:
                line = line.replace("z0ne", "zone") # edge case
                name, desc = parse_name_desc(line, "zone")
                queue.append((division, stop_name, name, desc, "zone"))
            elif n > 5 and line[:5] == "track":
                line = get_full_track_line(file, line)
                name, desc = parse_name_desc(line, "track")
                queue.append((division, stop_name, name, desc, "track"))
            elif n > 3 and line[:3] == "tk.":
                line = line.replace("tk.", "track ", 1)
                name, desc = parse_name_desc(line, "track")
                queue.append((division, stop_name, name, desc, "track"))
            elif n > sub_n and line[:sub_n] == "substation":
                substations = parse_section_items(file)
                for sub_station in substations:
                    queue.append((division, stop_name, sub_station,  None, "substation"))
            elif n > cbh_n and line[:cbh_n] == "circuit breaker house":
                cbhs = parse_section_items(file)
                for cbh in cbhs:
                    queue.append((division, stop_name, cbh, None, "CBH"))
            elif RE_PRINTCODE.match(line) and n < 10 :
                prefix, nums = RE_PRINTCODE.match(line).groups()
                queue.append((division, stop_name, prefix + "-" + nums, None, "incomplete"))
            else:
                unable_to_process.append({
                    "division": division,
                    "stop_name": stop_name,
                    "file_line" : line,
                    "reason": "not right"
                })
            if len(queue) >= batch_size:
                flush_queue(queue, division, output_dir)
 
def write_unprocessed(unprocessed, output_dir):
    """
    Write non-.txt files to a CSV log.
    """
    if not unprocessed:
        return
    out_path = os.path.join(output_dir, "unprocessed_files.csv")
    file_exists = os.path.exists(out_path)
    with open(out_path, "a", newline="", encoding="utf-8") as out_file:
        writer = csv.writer(out_file)
        if not file_exists:
            writer.writerow(["file_path"])
        for file_path in unprocessed:
            writer.writerow([file_path])

def write_unable_to_process(output_dir):
    """
    Write all rows that could not be processed to CSV.
    """
    if not unable_to_process:
        return
    out_path = os.path.join(output_dir, "unable_to_process.csv")
    file_exists = os.path.exists(out_path)
    fieldnames = ["division", "stop_name", "file_line", "reason"]
    with open(out_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(unable_to_process)
 
def iterate_folders(parent_path, division, batch_size=1000):
    """
    Walk through folders, process .txt files, and collect unprocessed files.
    """
    queue = []
    unprocessed = []
    if os.path.exists(os.path.join(OUT_DIR,f"{division}.csv")):
        print("remove old csv")
        return
 
    for root, _, files in os.walk(parent_path):
        if "dup" in root:
            continue

        if not files:
            continue
       
        for file_name in files:
           
            file_path = os.path.join(root, file_name)
            if file_name.lower().endswith(".txt"):
                parse_write(
                    file_path=file_path,
                    division=division,
                    output_dir=OUT_DIR,
                    queue=queue,
                    batch_size=batch_size,
                )
            else:
                unprocessed.append(file_path)
 
    # flush anything left
    flush_queue(queue, division, OUT_DIR)
    write_unprocessed(unprocessed, OUT_DIR)
 
if __name__ == "__main__":
    runs = {
        "BMT Passenger Station Power Limits" : "BMT",
        "IND Passenger Station Power Limits" : "IND",
        "IRT Passenger Station Power Limits" : "IRT"
    }
 
    os.makedirs(OUT_DIR, exist_ok=True)
 
    for parent_dir, division in runs.items():
        print(f"Started run for {parent_dir}")
        iterate_folders(parent_path=parent_dir, division=division)
    
    write_unable_to_process(OUT_DIR)
 
    print("Processing complete.")