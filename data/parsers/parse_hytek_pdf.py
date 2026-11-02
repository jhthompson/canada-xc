#!/usr/bin/env python3
"""Extract individual event results from a Hy-Tek Meet Manager PDF."""

import argparse
import csv
import re
import subprocess
from pathlib import Path

RESULT = re.compile(
    r"^\s*(\d+)\s+(.+?)\s{2,}(.+?)\s{2,}(\d{1,2}:\d{2}(?:\.\d+)?)\s*(\d+)?\s*$"
)
EVENT = re.compile(r"\.{3,}Event\s+\d+\s+(.+)|Event\s+\d+\s+(.+)")


def extract(pdf: Path) -> list[dict[str, str]]:
    text = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    rows = []
    event = ""
    individual_results = False

    for line in text.splitlines():
        match = EVENT.search(line)
        if match:
            event = (match.group(1) or match.group(2)).strip()
            individual_results = False
            continue
        if "Team Scores" in line:
            individual_results = False
        elif line.strip().startswith("Results -"):
            individual_results = True
        elif individual_results and (match := RESULT.match(line)):
            place, name, team, result, points = match.groups()
            year = ""
            rows.append(
                {
                    "event": event,
                    "place": place,
                    "name": name,
                    "year": year,
                    "team": team,
                    "result": result,
                    "points": points or "",
                }
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pdf", type=Path, help="Hy-Tek results PDF (requires pdftotext)"
    )
    parser.add_argument(
        "-o", "--output", type=Path, help="CSV output (default: alongside PDF)"
    )
    args = parser.parse_args()

    output = args.output or args.pdf.with_suffix(".csv")
    columns = ["event", "place", "name", "year", "team", "result", "points"]
    with output.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(extract(args.pdf))
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
