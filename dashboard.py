import csv
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Select
from bokeh.plotting import figure

DATA_FILE = "monthly_zip_response.csv"
MONTHS = [f"2020-{m:02d}" for m in range(1, 13)]

# Load precomputed averages.
data = {}
all_data = {}

with open(DATA_FILE, newline="", encoding="utf-8") as f:
    for row_data in csv.DictReader(f):
        month = row_data["month"]
        zipcode = row_data["zipcode"]
        average = float(row_data["average_hours"])

        if zipcode == "ALL":
            all_data[month] = average
        else:
            data[(month, zipcode)] = average

zipcodes = sorted({zipcode for _, zipcode in data})
if len(zipcodes) < 2:
    raise ValueError("Need at least two ZIP codes in the data.")

zip1 = Select(title="ZIP code 1", value=zipcodes[0], options=zipcodes)
zip2 = Select(
    title="ZIP code 2",
    value=zipcodes[1] if len(zipcodes) > 1 else zipcodes[0],
    options=zipcodes,
)

months = MONTHS

def series_for(zipcode):
    return [
        data.get((month, zipcode), float("nan"))
        for month in months
    ]

source_all = ColumnDataSource(data={
    "month": months,
    "hours": [all_data.get(month, float("nan")) for month in months],
})
source_zip1 = ColumnDataSource(data={
    "month": months,
    "hours": series_for(zip1.value),
})
source_zip2 = ColumnDataSource(data={
    "month": months,
    "hours": series_for(zip2.value),
})

plot = figure(
    title="Average 311 Complaint Resolution Time by Closure Month (2020)",
    x_range=months,
    width=1000,
    height=500,
    x_axis_label="Month complaint was closed",
    y_axis_label="Average resolution time (hours)",
    toolbar_location="above",
)
plot.line("month", "hours", source=source_all, line_width=3, legend_label="All ZIP codes")
plot.circle("month", "hours", source=source_all, size=6)
plot.line("month", "hours", source=source_zip1, line_width=2, legend_label="ZIP 1")
plot.circle("month", "hours", source=source_zip1, size=5)
plot.line("month", "hours", source=source_zip2, line_width=2, legend_label="ZIP 2")
plot.circle("month", "hours", source=source_zip2, size=5)
plot.xaxis.major_label_orientation = 0.8
plot.legend.location = "top_left"
plot.legend.click_policy = "hide"

def update(attr, old, new):
    source_zip1.data = {"month": months, "hours": series_for(zip1.value)}
    source_zip2.data = {"month": months, "hours": series_for(zip2.value)}

zip1.on_change("value", update)
zip2.on_change("value", update)

curdoc().add_root(column(row(zip1, zip2), plot))
curdoc().title = "NYC 311 ZIP Code Dashboard"
