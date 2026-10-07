"""
Unit tests for analyzer.py (business rules).

All tests use a fixed date so results are always deterministic.
"""
import os
import sys
import unittest
from datetime import date, timedelta

# Make the project folder importable, wherever the tests are run from
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import analyzer

# Fixed "today" used by every test
TODAY = date(2026, 10, 6)


def make_medicine(quantity=100, monthly_sales=10, expiry="2027-06-01",
                  reorder_level=10):
    """Build a minimal medicine dictionary for the tests."""
    return {
        "id": 1,
        "name": "Test Medicine",
        "batch": "TST01",
        "quantity": quantity,
        "expiry_date": expiry,
        "monthly_sales": monthly_sales,
        "reorder_level": reorder_level,
        "created_at": "2026-01-01",
    }


class ExpiryStatusTests(unittest.TestCase):
    """days_left < 0 -> Expired; <= 90 -> Nearing Expiry; else Safe."""

    def medicine_expiring_in(self, days):
        expiry = (TODAY + timedelta(days=days)).isoformat()
        return make_medicine(expiry=expiry)

    def test_expired_one_day_ago(self):
        med = self.medicine_expiring_in(-1)
        self.assertEqual(analyzer.expiry_status(med, TODAY), "Expired")

    def test_expiring_today_is_nearing_expiry(self):
        # days_left == 0 is NOT < 0, so today still counts as nearing expiry
        med = self.medicine_expiring_in(0)
        self.assertEqual(analyzer.expiry_status(med, TODAY), "Nearing Expiry")

    def test_boundary_90_days_is_nearing_expiry(self):
        med = self.medicine_expiring_in(90)
        self.assertEqual(analyzer.expiry_status(med, TODAY), "Nearing Expiry")

    def test_boundary_91_days_is_safe(self):
        med = self.medicine_expiring_in(91)
        self.assertEqual(analyzer.expiry_status(med, TODAY), "Safe")

    def test_days_until_expiry(self):
        med = self.medicine_expiring_in(24)
        self.assertEqual(analyzer.days_until_expiry(med, TODAY), 24)


class SalesRateTests(unittest.TestCase):
    """months_of_stock = quantity / monthly_sales."""

    def test_slow_when_more_than_six_months(self):
        med = make_medicine(quantity=70, monthly_sales=10)   # 7 months
        self.assertEqual(analyzer.sales_rate(med), "Slow")

    def test_exactly_six_months_is_moderate(self):
        med = make_medicine(quantity=60, monthly_sales=10)   # 6 months
        self.assertEqual(analyzer.sales_rate(med), "Moderate")

    def test_exactly_two_months_is_moderate(self):
        med = make_medicine(quantity=20, monthly_sales=10)   # 2 months
        self.assertEqual(analyzer.sales_rate(med), "Moderate")

    def test_just_under_two_months_is_fast(self):
        med = make_medicine(quantity=19, monthly_sales=10)   # 1.9 months
        self.assertEqual(analyzer.sales_rate(med), "Fast")

    def test_zero_monthly_sales_is_no_sales(self):
        med = make_medicine(quantity=50, monthly_sales=0)
        self.assertEqual(analyzer.sales_rate(med), "No Sales")


class ShortageTests(unittest.TestCase):
    """quantity <= reorder_level -> Shortage."""

    def test_quantity_equal_to_reorder_level_is_shortage(self):
        med = make_medicine(quantity=10, reorder_level=10)
        self.assertTrue(analyzer.has_shortage(med))

    def test_quantity_below_reorder_level_is_shortage(self):
        med = make_medicine(quantity=5, reorder_level=10)
        self.assertTrue(analyzer.has_shortage(med))

    def test_quantity_above_reorder_level_is_not_shortage(self):
        med = make_medicine(quantity=11, reorder_level=10)
        self.assertFalse(analyzer.has_shortage(med))


class RecommendedActionTests(unittest.TestCase):
    """The action rules in priority order."""

    def test_expired_medicine_is_removed(self):
        med = make_medicine(expiry="2026-01-01")
        self.assertEqual(analyzer.recommended_action(med, TODAY),
                         "Remove from stock")

    def test_nearing_and_slow_is_review_stock(self):
        med = make_medicine(quantity=120, monthly_sales=10,
                            expiry="2026-10-30")   # Slow (12 months)
        self.assertEqual(analyzer.recommended_action(med, TODAY),
                         "Review stock")

    def test_nearing_and_fast_is_prioritize(self):
        med = make_medicine(quantity=10, monthly_sales=60,
                            expiry="2026-11-01")   # Fast (~0.17 months)
        self.assertEqual(analyzer.recommended_action(med, TODAY),
                         "Prioritize sales / discount")

    def test_safe_but_shortage_is_reorder(self):
        med = make_medicine(quantity=5, monthly_sales=50,
                            expiry="2027-06-01", reorder_level=10)
        self.assertEqual(analyzer.recommended_action(med, TODAY), "Reorder")

    def test_safe_and_fine_needs_no_action(self):
        med = make_medicine(quantity=500, monthly_sales=60,
                            expiry="2027-08-15", reorder_level=100)
        self.assertEqual(analyzer.recommended_action(med, TODAY),
                         "No action needed")


class SampleMedicineTests(unittest.TestCase):
    """The exact sample required by the assignment."""

    def test_required_sample_output(self):
        med = {
            "id": 1,
            "name": "Amoxicillin",
            "batch": "AMX24",
            "quantity": 120,
            "expiry_date": "2026-10-30",   # 30-10-2026
            "monthly_sales": 10,
            "reorder_level": 30,
            "created_at": "2026-10-06",
        }
        result = analyzer.analyze(med, date(2026, 10, 6))
        self.assertEqual(result["expiry_status"], "Nearing Expiry")
        self.assertEqual(result["quantity"], 120)
        self.assertEqual(result["sales_rate"], "Slow")
        self.assertEqual(result["action"], "Review stock")
        self.assertEqual(result["days_left"], 24)


if __name__ == "__main__":
    unittest.main()