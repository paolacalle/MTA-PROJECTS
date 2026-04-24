import csv
import os
import re

OUT_DIR = "data_extracted/intial_processed"
DIVISIONS = ("BMT", "IRT", "IND")
OUTPUT_HEADERS = ["division", "stop_name", "name", "description", "category"]
UNABLE_HEADERS = ["division", "stop_name", "file_line", "reason"]

RE_PRINTCODE = re.compile(r"(\d{3})\s*-\s*(\d{1,2}(?:\s*,\s*\d{1,2})*)")


def flush_queue(queue, division, output_dir):
    """
    Append buffered parsed rows to the current division CSV.

    The parser writes in batches because a full division can span many source
    files, and the intermediate CSV is the handoff point for later scripts.
    """
    if not queue:
        return

    out_path = os.path.join(output_dir, f"{division}.csv")
    file_exists = os.path.exists(out_path)

    with open(out_path, "a", newline="", encoding="utf-8") as out_file:
        writer = csv.writer(out_file)
        if not file_exists:
            writer.writerow(OUTPUT_HEADERS)
        writer.writerows(queue)

    queue.clear()


def parse_section_items(file_obj):
    """
    Read lines after a section header until the parser sees enough blank lines.

    The blank-line tolerance is deliberate: some source files have extra spacing
    inside the section, so the parser only stops after repeated empty lines.
    """
    items = []
    blank_count = 0

    while True:
        next_line = file_obj.readline()
        if not next_line:
            break

        stripped = next_line.strip().lower()
        if stripped == "":
            if blank_count > 2:
                break
            blank_count += 1
            continue

        blank_count = 0
        items.append(stripped)

    return items


def get_full_track_line(file_obj, line):
    """
    Merge multiline track descriptions until two blank lines mark the end.
    """
    blank_count = 0

    while True:
        next_line = file_obj.readline()
        if next_line == "":
            raise Exception("sudden end of track")

        stripped = next_line.strip()
        if stripped == "":
            blank_count += 1
            if blank_count == 2:
                return line
            continue

        blank_count = 0
        line += " " + stripped.lower()


def parse_name_desc(line, line_type):
    """
    Split a raw zone/track line into identifier and description.

    Example:
    `track g1 - bumper block ...`
    becomes:
    (`track g1`, `bumper block ...`)
    """
    parts = [part for part in line.split(" ") if part]
    if len(parts) < 2:
        raise Exception(f"could not parse {line_type} line: {line}")

    if line_type not in parts[0] and line_type not in parts[1]:
        raise Exception(f"expected {line_type} to be first word. Got {parts[0]}. Line {line}")

    if "-" in parts[0]:
        split_identifier = parts[0].split("-", 2)
        if len(split_identifier) < 2 or not (1 <= len(split_identifier[1]) <= 2):
            raise Exception(f"expected {line_type}-## {parts[0]}")

        identifier = split_identifier[0] + " " + split_identifier[1]
        if line_type == "zone" and "," in identifier:
            return identifier + parts[1], " ".join(parts[2:])
        return identifier, " ".join(parts[1:])

    if len(parts) > 2 and parts[1] == "-":
        return parts[0] + " " + parts[2], " ".join(parts[3:])

    return parts[0] + " " + parts[1], " ".join(parts[2:])


def append_unable_to_process(unable_to_process, division, stop_name, line, reason="not right"):
    """
    Record a raw line that did not match any of the supported parsing cases.
    """
    unable_to_process.append(
        {
            "division": division,
            "stop_name": stop_name,
            "file_line": line,
            "reason": reason,
        }
    )


def parse_write(file_path, division, output_dir, queue, unable_to_process, batch_size=1000):
    """
    Parse one raw station file into normalized intermediate rows.

    This function preserves the current case-specific rules for zones, tracks,
    `tk.` abbreviations, substation sections, CBH sections, and short
    standalone print-code lines that represent incomplete files.
    """
    stop_name = os.path.splitext(os.path.basename(file_path))[0]

    with open(file_path, "r", encoding="utf-8") as file:
        while True:
            raw_line = file.readline()
            if not raw_line:
                break

            line = raw_line.strip().lower()
            if line == "":
                continue

            if line.startswith("zone") or line.startswith("z0ne"):
                line = line.replace("z0ne", "zone", 1)
                name, desc = parse_name_desc(line, "zone")
                queue.append((division, stop_name, name, desc, "zone"))
            elif line.startswith("track"):
                full_line = get_full_track_line(file, line)
                name, desc = parse_name_desc(full_line, "track")
                queue.append((division, stop_name, name, desc, "track"))
            elif line.startswith("tk."):
                normalized = line.replace("tk.", "track ", 1)
                name, desc = parse_name_desc(normalized, "track")
                queue.append((division, stop_name, name, desc, "track"))
            elif line.startswith("substation"):
                for substation in parse_section_items(file):
                    queue.append((division, stop_name, substation, None, "substation"))
            elif line.startswith("circuit breaker house"):
                for cbh in parse_section_items(file):
                    queue.append((division, stop_name, cbh, None, "CBH"))
            elif RE_PRINTCODE.fullmatch(line) and len(line) < 10:
                prefix, nums = RE_PRINTCODE.fullmatch(line).groups()
                queue.append((division, stop_name, f"{prefix}-{nums}", None, "incomplete"))
            else:
                append_unable_to_process(unable_to_process, division, stop_name, line)

            if len(queue) >= batch_size:
                flush_queue(queue, division, output_dir)


def write_unprocessed(unprocessed, output_dir):
    """
    Log files that were skipped because they were not source `.txt` inputs.
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


def write_unable_to_process(unable_to_process, output_dir):
    """
    Write the per-line parse failures captured during the extraction stage.
    """
    if not unable_to_process:
        return

    out_path = os.path.join(output_dir, "unable_to_process.csv")
    file_exists = os.path.exists(out_path)

    with open(out_path, "a", newline="", encoding="utf-8") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=UNABLE_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerows(unable_to_process)


def iterate_folders(parent_path, division, batch_size=1000):
    """
    Walk one division directory and run the stage-one extraction pipeline.

    Any path containing `dup` is skipped intentionally because those folders
    represent duplicate source material that should not be re-processed.
    """
    queue = []
    unprocessed = []
    unable_to_process = []

    out_path = os.path.join(OUT_DIR, f"{division}.csv")
    if os.path.exists(out_path):
        print(f"Skipping {division}: remove existing output first: {out_path}")
        return

    for root, _, files in os.walk(parent_path):
        if "dup" in root:
            continue

        for file_name in files:
            file_path = os.path.join(root, file_name)
            if file_name.lower().endswith(".txt"):
                parse_write(
                    file_path=file_path,
                    division=division,
                    output_dir=OUT_DIR,
                    queue=queue,
                    unable_to_process=unable_to_process,
                    batch_size=batch_size,
                )
            else:
                unprocessed.append(file_path)

    flush_queue(queue, division, OUT_DIR)
    write_unprocessed(unprocessed, OUT_DIR)
    write_unable_to_process(unable_to_process, OUT_DIR)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)

    for division in DIVISIONS:
        source_dir = division
        if os.path.isdir(source_dir):
            print(f"Processing {division} from {source_dir}...")
            iterate_folders(source_dir, division)
        else:
            print(f"Skipping {division}: source directory not found at {source_dir}")
