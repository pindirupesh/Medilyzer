"""
validators.py
--------------
Small helper functions that check user input before it is used.

Each function either returns a normal value or raises ValueError with a
friendly message, so main.py can catch ValueError and simply ask again.
Dates are typed by the user as DD-MM-YYYY but stored as ISO YYYY-MM-DD.
"""
import re
from datetime import date

# Exactly: two digits, dash, two digits, dash, four digits
DATE_PATTERN = re.compile(r"^\d{2}-\d{2}-\d{4}$")


def parse_date(text):
    """Parse a date given as DD-MM-YYYY and return a datetime.date.

    Rejects wrong formats and impossible dates like 31-02-2026.
    """
    text = text.strip()
    if not DATE_PATTERN.match(text):
        raise ValueError("Date must be in DD-MM-YYYY format, e.g. 30-10-2026.")
    day, month, year = (int(part) for part in text.split("-"))
    try:
        return date(year, month, day)   # raises ValueError for impossible dates
    except ValueError:
        raise ValueError("'" + text + "' is not a real calendar date.")


def to_iso(text):
    """Convert DD-MM-YYYY to the ISO string (YYYY-MM-DD) used for storage."""
    return parse_date(text).isoformat()


def format_date(iso_text):
    """Convert an ISO date string (YYYY-MM-DD) back to DD-MM-YYYY."""
    return date.fromisoformat(iso_text).strftime("%d-%m-%Y")


def is_past(iso_text, today):
    """True when the ISO date is before 'today' (medicine already expired)."""
    return date.fromisoformat(iso_text) < today


def validate_non_empty(text, label="Value"):
    """Reject empty or whitespace-only names / batches."""
    text = text.strip()
    if not text:
        raise ValueError(label + " cannot be empty.")
    return text


def validate_positive_int(text, label="Number"):
    """Return a whole number > 0 (for quantities and IDs)."""
    text = text.strip()
    if not text.isdigit():          # rejects '', '-5', '5.5', 'abc'
        raise ValueError(label + " must be a whole number greater than 0.")
    value = int(text)
    if value <= 0:
        raise ValueError(label + " must be greater than 0.")
    return value


def validate_quantity(text, label="Quantity"):
    """Return a positive quantity (non-positive quantities are rejected)."""
    return validate_positive_int(text, label)


def validate_non_negative_int(text, label="Number"):
    """Return a whole number >= 0 (monthly sales / reorder level may be 0)."""
    text = text.strip()
    if not text.isdigit():
        raise ValueError(label + " must be a whole number of 0 or more.")
    return int(text)