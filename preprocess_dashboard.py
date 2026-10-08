import csv
import json
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime

BASE = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
OUTPUT = "monthly_zip_response.csv"
LIMIT = 50000

stats = defaultdict(lambda: [0.0, 0])
offset = 0
valid = 0

while True:
    params = {
        "$select": "created_date,closed_date,incident_zip",
        "$where": (
            'created_date >= "2020-01-01T00:00:00" AND '
            'created_date < "2021-01-01T00:00:00" AND '
            "closed_date IS NOT NULL AND incident_zip IS NOT NULL"
        ),
        "$limit": LIMIT,
        "$offset": offset,
        "$order": "created_date"
    }

    url = BASE + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url, headers={"User-Agent": "COMP370-homework"}
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        batch = json.loads(response.read().decode("utf-8"))

    if not batch:
        break

    for row in batch:
        try:
            created = datetime.fromisoformat(row["created_date"])
            closed = datetime.fromisoformat(row["closed_date"])
            zipcode = row["incident_zip"].strip()

            if not zipcode or closed < created:
                continue

            month = closed.strftime("%Y-%m")
            hours = (closed - created).total_seconds() / 3600
            stats[(month, zipcode)][0] += hours
            stats[(month, zipcode)][1] += 1
            valid += 1
        except (KeyError, ValueError, AttributeError):
            continue

    offset += len(batch)
    print(f"Downloaded {offset:,} records; valid: {valid:,}", flush=True)

    if len(batch) < LIMIT:
        break

monthly_totals = defaultdict(lambda: [0.0, 0])

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["month", "zipcode", "average_hours", "count"])

    for (month, zipcode), (total, count) in sorted(stats.items()):
        writer.writerow([month, zipcode, round(total / count, 3), count])
        monthly_totals[month][0] += total
        monthly_totals[month][1] += count

    for month, (total, count) in sorted(monthly_totals.items()):
        writer.writerow([month, "ALL", round(total / count, 3), count])

print(f"Finished. Valid records: {valid:,}")
print(f"Created {OUTPUT}")
