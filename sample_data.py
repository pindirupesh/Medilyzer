"""
sample_data.py
--------------
Seeds the in-memory inventory with 10+ realistic medicines so the program
is useful immediately after start-up.

The required sample medicine is #1:
    Amoxicillin, batch AMX24, quantity 120,
    expiry 30-10-2026, monthly sales 10

The other medicines were chosen so every business rule gets exercised:
expired stock, nearing expiry, safe stock, slow/fast/no sales, shortage.
"""
from datetime import date


def seed_medicines():
    """Return a fresh list of sample medicine dictionaries."""
    today_iso = date.today().isoformat()

    # (id, name, batch, quantity, expiry ISO, monthly_sales, reorder_level)
    rows = [
        (1,  "Amoxicillin 500mg",    "AMX24",  120, "2026-10-30",  10,  30),
        (2,  "Paracetamol 500mg",    "PCM500", 500, "2027-08-15", 120, 100),
        (3,  "Vitamin C 500mg",      "VTC10",  200, "2026-06-01",  15,  50),
        (4,  "Ibuprofen 400mg",      "IBU22",   80, "2026-11-20",   8,  20),
        (5,  "Cetirizine 10mg",      "CTZ05",   15, "2027-01-10",   0,  20),
        (6,  "Azithromycin 500mg",   "AZT31",   45, "2026-12-15",  20,  25),
        (7,  "Insulin Glargine",     "INS07",   10, "2026-11-05",   3,  12),
        (8,  "ORS Sachet",           "ORS20",  300, "2028-01-31",  60, 100),
        (9,  "Cough Syrup 100ml",    "CSY12",   25, "2027-03-31",  30,  10),
        (10, "Pantoprazole 40mg",    "PNT40",   40, "2026-11-02",  40,  20),
        (11, "Metformin 500mg",      "MET500",  60, "2027-05-31",   6,  30),
    ]

    medicines = []
    for (med_id, name, batch, qty, expiry, sales, reorder) in rows:
        medicines.append({
            "id": med_id,
            "name": name,
            "batch": batch,
            "quantity": qty,
            "expiry_date": expiry,
            "monthly_sales": sales,
            "reorder_level": reorder,
            "created_at": today_iso,
        })
    return medicines


def seed_transactions():
    """Return a few sample purchase/sale records (history)."""
    # (id, medicine_id, type, quantity, date ISO)
    rows = [
        (1, 1, "PURCHASE", 100, "2026-09-01"),
        (2, 1, "SALE",      30, "2026-09-15"),
        (3, 2, "SALE",      80, "2026-09-20"),
        (4, 3, "PURCHASE",  50, "2026-05-10"),
        (5, 8, "SALE",     120, "2026-10-01"),
    ]
    return [
        {"id": tx_id, "medicine_id": med_id, "type": tx_type,
         "quantity": qty, "date": day}
        for (tx_id, med_id, tx_type, qty, day) in rows
    ]