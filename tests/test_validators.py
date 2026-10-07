"""
Unit tests for validators.py (input validation).
"""
import os
import sys
import unittest
from datetime import date

# Make the project folder importable, wherever the tests are run from
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validators import (
    format_date,
    is_past,
    parse_date,
    to_iso,
    validate_non_empty,
    validate_non_negative_int,
    validate_quantity,
)


class ParseDateTests(unittest.TestCase):
    """Dates must be DD-MM-YYYY and must be real calendar dates."""

    def test_valid_date(self):
        self.assertEqual(parse_date("30-10-2026"), date(2026, 10, 30))

    def test_valid_date_with_spaces_is_trimmed(self):
        self.assertEqual(parse_date("  01-01-2027  "), date(2027, 1, 1))

    def test_rejects_impossible_day(self):
        with self.assertRaises(ValueError):
            parse_date("31-02-2026")

    def test_rejects_day_32(self):
        with self.assertRaises(ValueError):
            parse_date("32-01-2026")

    def test_rejects_month_13(self):
        with self.assertRaises(ValueError):
            parse_date("10-13-2026")

    def test_rejects_wrong_separator(self):
        with self.assertRaises(ValueError):
            parse_date("30/10/2026")

    def test_rejects_short_year(self):
        with self.assertRaises(ValueError):
            parse_date("30-10-26")

    def test_rejects_letters(self):
        with self.assertRaises(ValueError):
            parse_date("abc")

    def test_rejects_empty_string(self):
        with self.assertRaises(ValueError):
            parse_date("")


class DateFormattingTests(unittest.TestCase):

    def test_to_iso(self):
        self.assertEqual(to_iso("30-10-2026"), "2026-10-30")

    def test_format_date_back_to_display(self):
        self.assertEqual(format_date("2026-10-30"), "30-10-2026")

    def test_round_trip(self):
        self.assertEqual(format_date(to_iso("15-08-2027")), "15-08-2027")


class IsPastTests(unittest.TestCase):

    def test_past_date_is_past(self):
        self.assertTrue(is_past("2026-06-01", date(2026, 10, 6)))

    def test_future_date_is_not_past(self):
        self.assertFalse(is_past("2027-01-01", date(2026, 10, 6)))

    def test_today_is_not_past(self):
        self.assertFalse(is_past("2026-10-06", date(2026, 10, 6)))


class QuantityTests(unittest.TestCase):
    """Quantities must be whole numbers greater than 0."""

    def test_valid_quantity(self):
        self.assertEqual(validate_quantity("120"), 120)

    def test_one_is_valid(self):
        self.assertEqual(validate_quantity("1"), 1)

    def test_zero_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_quantity("0")

    def test_negative_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_quantity("-5")

    def test_text_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_quantity("abc")

    def test_decimal_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_quantity("5.5")

    def test_empty_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_quantity("")


class NonNegativeIntTests(unittest.TestCase):
    """Monthly sales / reorder level may be 0 but not negative."""

    def test_zero_is_valid(self):
        self.assertEqual(validate_non_negative_int("0"), 0)

    def test_positive_is_valid(self):
        self.assertEqual(validate_non_negative_int("30"), 30)

    def test_negative_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_non_negative_int("-1")


class NonEmptyTests(unittest.TestCase):
    """Names and batches cannot be empty."""

    def test_normal_name_is_valid(self):
        self.assertEqual(validate_non_empty("Amoxicillin", "Name"), "Amoxicillin")

    def test_empty_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_non_empty("", "Name")

    def test_spaces_only_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_non_empty("   ", "Name")


if __name__ == "__main__":
    unittest.main()