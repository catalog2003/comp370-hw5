#!/usr/bin/env python3
import argparse
import csv
import sys
from collections import Counter
from datetime import datetime

def parse_date(value):
    return datetime.strptime(value, "%m/%d/%Y").date()

def main():
    parser = argparse.ArgumentParser(
        description="Count NYC 311 complaint types by borough within a creation-date range."
    )
    parser.add_argument("-i", required=True, help="Input CSV file")
    parser.add_argument("-s", required=True, help="Start date (MM/DD/YYYY)")
    parser.add_argument("-e", required=True, help="End date (MM/DD/YYYY)")
    parser.add_argument("-o", help="Output CSV file (default: stdout)")
    args = parser.parse_args()

    try:
        start = parse_date(args.s)
        end = parse_date(args.e)
    except ValueError:
        parser.error("Dates must use MM/DD/YYYY format, e.g. 01/01/2024")

    if start > end:
        parser.error("Start date must be on or before end date.")

    counts = Counter()

    with open(args.i, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                created = datetime.strptime(
                    row["Created Date"].strip(), "%m/%d/%Y %I:%M:%S %p"
                ).date()
            except (ValueError, AttributeError):
                continue

            if start <= created <= end:
                complaint = (row.get("Complaint Type") or "").strip()
                borough = (row.get("Borough") or "").strip()

                if complaint and borough:
                    counts[(complaint, borough)] += 1

    output = open(args.o, "w", newline="", encoding="utf-8") if args.o else sys.stdout
    try:
        writer = csv.writer(output)
        writer.writerow(["complaint type", "borough", "count"])
        for (complaint, borough), count in sorted(counts.items()):
            writer.writerow([complaint, borough.title(), count])
    finally:
        if args.o:
            output.close()

if __name__ == "__main__":
    main()
