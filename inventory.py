"""
inventory.py
------------
The storage layer of the program. Instead of a database we keep two plain
Python lists of dictionaries in memory:

    medicine = {
        "id": 1,
        "name": "Amoxicillin",
        "batch": "AMX24",
        "quantity": 120,
        "expiry_date": "2026-10-30",   # ISO YYYY-MM-DD
        "monthly_sales": 10,
        "reorder_level": 30,
        "created_at": "2026-10-06",
    }

    transaction = {
        "id": 1, "medicine_id": 1, "type": "SALE",
        "quantity": 30, "date": "2026-09-15",
    }

Every function receives these lists as an argument, so nothing is hidden.
Note: data is lost when the program exits; sample_data.py re-seeds it.
"""
from analyzer import expiry_status


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def next_id(medicines):
    """New unique id: highest existing id + 1 (or 1 when the list is empty)."""
    if not medicines:
        return 1
    return max(m["id"] for m in medicines) + 1


def get_medicine(medicines, medicine_id):
    """Return the medicine with this id, or None if it does not exist."""
    for medicine in medicines:
        if medicine["id"] == medicine_id:
            return medicine
    return None


# ---------------------------------------------------------------------------
# Add / update
# ---------------------------------------------------------------------------
def add_medicine(medicines, medicine):
    """Append a medicine. The (name, batch) pair must be unique."""
    for existing in medicines:
        if (existing["name"].lower() == medicine["name"].lower()
                and existing["batch"].upper() == medicine["batch"].upper()):
            raise ValueError(
                "A medicine named '" + medicine["name"] +
                "' with batch '" + medicine["batch"] + "' already exists.")
    medicines.append(medicine)
    return medicine


def update_expiry(medicines, medicine_id, iso_date):
    """Replace the expiry date of one medicine (ISO format)."""
    medicine = get_medicine(medicines, medicine_id)
    if medicine is None:
        raise ValueError("No medicine found with ID " + str(medicine_id) + ".")
    medicine["expiry_date"] = iso_date
    return medicine


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------
def search_by_name(medicines, term):
    """Partial, case-insensitive match on the medicine name."""
    term = term.strip().lower()
    return [m for m in medicines if term in m["name"].lower()]


def search_by_batch(medicines, term):
    """Partial, case-insensitive match on the batch code."""
    term = term.strip().lower()
    return [m for m in medicines if term in m["batch"].lower()]


def filter_by_status(medicines, status, today):
    """All medicines whose expiry status equals 'Expired'/'Nearing Expiry'/'Safe'."""
    return [m for m in medicines if expiry_status(m, today) == status]


# ---------------------------------------------------------------------------
# Purchases and sales (these change the stock!)
# ---------------------------------------------------------------------------
def add_transaction(transactions, medicine_id, tx_type, quantity, iso_date):
    """Append a PURCHASE or SALE record and return it."""
    tx_id = 1 if not transactions else max(t["id"] for t in transactions) + 1
    transaction = {
        "id": tx_id,
        "medicine_id": medicine_id,
        "type": tx_type,
        "quantity": quantity,
        "date": iso_date,
    }
    transactions.append(transaction)
    return transaction


def record_purchase(medicines, transactions, medicine_id, quantity, iso_date):
    """Increase stock after a purchase."""
    medicine = get_medicine(medicines, medicine_id)
    if medicine is None:
        raise ValueError("No medicine found with ID " + str(medicine_id) + ".")
    medicine["quantity"] += quantity
    add_transaction(transactions, medicine_id, "PURCHASE", quantity, iso_date)
    return medicine


def record_sale(medicines, transactions, medicine_id, quantity, iso_date):
    """Decrease stock after a sale.

    - Blocks the sale when there is not enough stock (raises ValueError).
    - Adds the sold amount to monthly_sales so the sales rate stays realistic.
    """
    medicine = get_medicine(medicines, medicine_id)
    if medicine is None:
        raise ValueError("No medicine found with ID " + str(medicine_id) + ".")
    if quantity > medicine["quantity"]:
        raise ValueError(
            "Insufficient stock: only " + str(medicine["quantity"]) +
            " unit(s) of " + medicine["name"] + " available.")
    medicine["quantity"] -= quantity
    medicine["monthly_sales"] += quantity
    add_transaction(transactions, medicine_id, "SALE", quantity, iso_date)
    return medicine