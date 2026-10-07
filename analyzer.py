"""
analyzer.py
-----------
Business rules for the Medicine Expiry and Inventory Analyzer.

Every function here is a simple "pure" function: it receives the medicine
data and the current date, and just returns an answer. It never changes
data and never reads the system clock, which makes it very easy to test.

All thresholds are defined as constants at the top of this file so they
are easy to find and change.
"""
from datetime import date

# ---------------------------------------------------------------------------
# Business rule constants
# ---------------------------------------------------------------------------
EXPIRY_NEARING_DAYS = 90     # days_left <= 90              -> "Nearing Expiry"
SLOW_MONTHS = 6              # months_of_stock > 6          -> "Slow"
MODERATE_MIN_MONTHS = 2      # 2 <= months_of_stock <= 6    -> "Moderate"
                             # months_of_stock < 2          -> "Fast"

# Action labels kept in one place so menu and reports always agree
ACTION_REMOVE = "Remove from stock"
ACTION_REVIEW = "Review stock"
ACTION_PRIORITIZE = "Prioritize sales / discount"
ACTION_REORDER = "Reorder"
ACTION_NONE = "No action needed"


def days_until_expiry(medicine, today):
    """Days until the medicine expires. Negative value = already expired."""
    expiry = date.fromisoformat(medicine["expiry_date"])
    return (expiry - today).days


def expiry_status(medicine, today):
    """Return 'Expired', 'Nearing Expiry' or 'Safe'."""
    days_left = days_until_expiry(medicine, today)
    if days_left < 0:
        return "Expired"
    if days_left <= EXPIRY_NEARING_DAYS:
        return "Nearing Expiry"
    return "Safe"


def sales_rate(medicine):
    """Return 'No Sales', 'Slow', 'Moderate' or 'Fast'.

    months_of_stock = quantity / monthly_sales
    """
    monthly_sales = medicine["monthly_sales"]
    if monthly_sales <= 0:
        return "No Sales"
    months_of_stock = medicine["quantity"] / monthly_sales
    if months_of_stock > SLOW_MONTHS:
        return "Slow"
    if months_of_stock >= MODERATE_MIN_MONTHS:
        return "Moderate"
    return "Fast"


def has_shortage(medicine):
    """True when stock has fallen to (or below) the reorder level."""
    return medicine["quantity"] <= medicine["reorder_level"]


def recommended_action(medicine, today):
    """Rules are checked in priority order, top to bottom."""
    status = expiry_status(medicine, today)
    rate = sales_rate(medicine)

    if status == "Expired":
        return ACTION_REMOVE
    if status == "Nearing Expiry" and rate == "Slow":
        return ACTION_REVIEW
    if status == "Nearing Expiry":
        return ACTION_PRIORITIZE
    if has_shortage(medicine):
        return ACTION_REORDER
    return ACTION_NONE


def analyze(medicine, today):
    """Bundle every result for one medicine into a single dictionary."""
    return {
        "expiry_status": expiry_status(medicine, today),
        "quantity": medicine["quantity"],
        "sales_rate": sales_rate(medicine),
        "shortage": has_shortage(medicine),
        "action": recommended_action(medicine, today),
        "days_left": days_until_expiry(medicine, today),
    }