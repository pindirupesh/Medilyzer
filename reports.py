"""
reports.py
-----------
Everything that prints reports to the console, plus CSV / TXT export.
All exported files are written into an "exports/" folder (created
automatically the first time you export).
"""
import csv
import os
from datetime import datetime

from analyzer import analyze
from validators import format_date

EXPORT_FOLDER = "exports"


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------
def print_analysis_block(medicine, today):
    """Print the standard 4-line analysis block for one medicine."""
    result = analyze(medicine, today)
    print("  Expiry Status: " + result["expiry_status"])
    print("  Current Stock: " + str(result["quantity"]))
    print("  Sales Rate: " + result["sales_rate"])
    print("  Action: " + result["action"])


def print_medicine(medicine, today):
    """Print a heading line followed by the analysis block."""
    print("")
    print(str(medicine["id"]) + ". " + medicine["name"] +
          " (Batch: " + medicine["batch"] + ")  Expiry: " +
          format_date(medicine["expiry_date"]))
    print_analysis_block(medicine, today)


def print_medicine_list(medicines, today, heading="MEDICINES"):
    """Print every medicine with its analysis block."""
    print("")
    print("========== " + heading + " (" + str(len(medicines)) + ") ==========")
    if not medicines:
        print("  No medicines found.")
        return
    for medicine in medicines:
        print_medicine(medicine, today)


def print_expiry_report(medicines, today):
    """Expiry report grouped as Expired / Nearing Expiry / Safe."""
    groups = {"Expired": [], "Nearing Expiry": [], "Safe": []}
    for medicine in medicines:
        groups[analyze(medicine, today)["expiry_status"]].append(medicine)

    print("")
    print("========== EXPIRY REPORT (" + format_date(today.isoformat()) + ") ==========")

    print("")
    print("-- Expired (" + str(len(groups["Expired"])) + ") --")
    for medicine in groups["Expired"]:
        print("  " + medicine["name"] + " (Batch: " + medicine["batch"] +
              ") expired on " + format_date(medicine["expiry_date"]) +
              " -> Remove from stock")

    print("")
    print("-- Nearing Expiry (" + str(len(groups["Nearing Expiry"])) + ") --")
    for medicine in groups["Nearing Expiry"]:
        result = analyze(medicine, today)
        print("  " + medicine["name"] + " (Batch: " + medicine["batch"] +
              ") expires in " + str(result["days_left"]) +
              " day(s) -> " + result["action"])

    print("")
    print("-- Safe (" + str(len(groups["Safe"])) + ") --")
    for medicine in groups["Safe"]:
        print("  " + medicine["name"] + " (Batch: " + medicine["batch"] +
              ") expires on " + format_date(medicine["expiry_date"]))


def print_analysis_report(medicines, today):
    """Analysis report: nearing expiry, slow-moving stock, shortages."""
    results = [(m, analyze(m, today)) for m in medicines]
    nearing = [(m, r) for (m, r) in results if r["expiry_status"] == "Nearing Expiry"]
    slow = [(m, r) for (m, r) in results if r["sales_rate"] == "Slow"]
    shortages = [(m, r) for (m, r) in results if r["shortage"]]

    print("")
    print("========== ANALYSIS REPORT ==========")

    print("")
    print("1) Medicines nearing expiry:")
    if not nearing:
        print("   None.")
    for (medicine, result) in nearing:
        print("   - " + medicine["name"] + " (Batch: " + medicine["batch"] +
              "): " + str(result["days_left"]) + " day(s) left -> " +
              result["action"])

    print("")
    print("2) Slow-moving stock:")
    if not slow:
        print("   None.")
    for (medicine, result) in slow:
        months = medicine["quantity"] / medicine["monthly_sales"]
        print("   - " + medicine["name"] + " (Batch: " + medicine["batch"] +
              "): " + ("%.1f" % months) + " month(s) of stock -> " +
              result["action"])

    print("")
    print("3) Stock shortages:")
    if not shortages:
        print("   None.")
    for (medicine, result) in shortages:
        print("   - " + medicine["name"] + " (Batch: " + medicine["batch"] +
              "): " + str(medicine["quantity"]) + " left, reorder level " +
              str(medicine["reorder_level"]) + " -> " + result["action"])


# ---------------------------------------------------------------------------
# Row builders (list of dictionaries -> easy to write as CSV or TXT)
# ---------------------------------------------------------------------------
def medicine_rows(medicines, today):
    """Full detail row for every medicine."""
    rows = []
    for medicine in medicines:
        result = analyze(medicine, today)
        rows.append({
            "ID": medicine["id"],
            "Name": medicine["name"],
            "Batch": medicine["batch"],
            "Quantity": medicine["quantity"],
            "Expiry Date": format_date(medicine["expiry_date"]),
            "Monthly Sales": medicine["monthly_sales"],
            "Reorder Level": medicine["reorder_level"],
            "Expiry Status": result["expiry_status"],
            "Sales Rate": result["sales_rate"],
            "Shortage": "Yes" if result["shortage"] else "No",
            "Action": result["action"],
        })
    return rows


def expiry_rows(medicines, today):
    """Expiry-focused rows, sorted by expiry date (soonest first)."""
    ordered = sorted(medicines, key=lambda m: m["expiry_date"])
    rows = []
    for medicine in ordered:
        result = analyze(medicine, today)
        rows.append({
            "Name": medicine["name"],
            "Batch": medicine["batch"],
            "Expiry Date": format_date(medicine["expiry_date"]),
            "Days Left": result["days_left"],
            "Expiry Status": result["expiry_status"],
            "Action": result["action"],
        })
    return rows


def analysis_rows(medicines, today):
    """Only medicines that need attention, with every issue listed."""
    rows = []
    for medicine in medicines:
        result = analyze(medicine, today)
        issues = []
        if result["expiry_status"] == "Nearing Expiry":
            issues.append("Expires in " + str(result["days_left"]) + " day(s)")
        if result["sales_rate"] == "Slow":
            issues.append("Slow-moving stock")
        if result["shortage"]:
            issues.append("Low stock / shortage")
        if issues:
            rows.append({
                "Name": medicine["name"],
                "Batch": medicine["batch"],
                "Quantity": medicine["quantity"],
                "Sales Rate": result["sales_rate"],
                "Issue": "; ".join(issues),
                "Suggested Action": result["action"],
            })
    return rows


# ---------------------------------------------------------------------------
# Export to exports/ folder
# ---------------------------------------------------------------------------
def export_rows(rows, report_name, file_format):
    """Write rows (list of dicts) to exports/<report>_<timestamp>.<ext>.

    file_format is 'CSV' or 'TXT'. Returns the file path, or None if empty.
    """
    if not rows:
        return None
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = "csv" if file_format == "CSV" else "txt"
    path = os.path.join(EXPORT_FOLDER,
                        report_name + "_" + stamp + "." + extension)
    headers = list(rows[0].keys())

    if file_format == "CSV":
        with open(path, "w", newline="", encoding="utf-8") as out_file:
            writer = csv.DictWriter(out_file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)
    else:  # TXT - simple aligned columns
        widths = {}
        for header in headers:
            widest = len(str(header))
            for row in rows:
                widest = max(widest, len(str(row[header])))
            widths[header] = widest
        with open(path, "w", encoding="utf-8") as out_file:
            out_file.write("  ".join(str(h).ljust(widths[h]) for h in headers) + "\n")
            out_file.write("  ".join("-" * widths[h] for h in headers) + "\n")
            for row in rows:
                out_file.write("  ".join(str(row[h]).ljust(widths[h]) for h in headers) + "\n")
    return path
