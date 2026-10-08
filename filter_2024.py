import csv
from datetime import datetime

source = "311_Service_Requests_from_2010_to_Present_20250928.csv"
output = "nyc_311_2024.csv"

kept = 0
checked = 0

with open(source, "r", newline="", encoding="utf-8-sig") as infile, \
     open(output, "w", newline="", encoding="utf-8") as outfile:

    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        checked += 1
        created = row.get("Created Date", "").strip()
        zipcode = row.get("Incident Zip", "").strip()

        if not zipcode or not created:
            continue

        try:
            date = datetime.strptime(created, "%m/%d/%Y %I:%M:%S %p")
        except ValueError:
            continue

        if date.year == 2024:
            writer.writerow(row)
            kept += 1

        if checked % 1000000 == 0:
            print(f"Checked {checked:,} rows; kept {kept:,}")

print(f"Finished. Checked {checked:,} rows; kept {kept:,} rows.")
print(f"Output: {output}")
