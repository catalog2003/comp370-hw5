import csv

for filename in ["jan_feb.csv", "jun_jul.csv"]:
    total = 0
    with open(filename, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["complaint type"].strip().lower() == "illegal parking":
                total += int(row["count"])
    print(f"{filename}: {total:,} Illegal Parking complaints")
