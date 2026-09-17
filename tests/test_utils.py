import unittest
from datetime import date, datetime
from decimal import Decimal

from utils import format_datetime, format_money, get_period_range, normalize_name, parse_money


class MoneyTests(unittest.TestCase):
    def test_parses_brazilian_money(self):
        self.assertEqual(parse_money("R$ 1.234,50"), Decimal("1234.50"))

    def test_parses_simple_money(self):
        self.assertEqual(parse_money("12,90"), Decimal("12.90"))

    def test_rejects_invalid_money(self):
        self.assertIsNone(parse_money("abc"))

    def test_rejects_non_finite_and_out_of_range_money(self):
        for value in ("NaN", "sNaN", "Infinity", "-Infinity", "1e1000000", "100000000"):
            with self.subTest(value=value):
                self.assertIsNone(parse_money(value))

    def test_formats_brazilian_money(self):
        self.assertEqual(format_money(1234.5), "R$ 1.234,50")


class DateTests(unittest.TestCase):
    def test_formats_datetime_as_required(self):
        value = datetime(2026, 9, 9, 14, 5)
        self.assertEqual(format_datetime(value), "14:05  09/09/2026")

    def test_daily_period(self):
        result = get_period_range("daily", date(2026, 9, 9))
        self.assertEqual(result["start"], datetime(2026, 9, 9, 0, 0))
        self.assertEqual(result["end"], datetime(2026, 9, 10, 0, 0))
        self.assertEqual(result["previous_start"], datetime(2026, 9, 8, 0, 0))

    def test_weekly_period_starts_on_monday(self):
        result = get_period_range("weekly", date(2026, 9, 9))
        self.assertEqual(result["start"], datetime(2026, 9, 7, 0, 0))
        self.assertEqual(result["end"], datetime(2026, 9, 14, 0, 0))

    def test_monthly_period_crosses_year(self):
        result = get_period_range("monthly", date(2026, 12, 20))
        self.assertEqual(result["start"], datetime(2026, 12, 1, 0, 0))
        self.assertEqual(result["end"], datetime(2027, 1, 1, 0, 0))

    def test_previous_month_uses_calendar_boundaries(self):
        for current, expected in ((date(2026, 3, 15), datetime(2026, 2, 1)),
                                  (date(2024, 3, 1), datetime(2024, 2, 1)),
                                  (date(2026, 1, 2), datetime(2025, 12, 1))):
            with self.subTest(current=current):
                self.assertEqual(get_period_range("monthly", current)["previous_start"], expected)


class TextTests(unittest.TestCase):
    def test_normalizes_name(self):
        self.assertEqual(normalize_name("  Café   Duplo  "), "café duplo")


if __name__ == "__main__":
    unittest.main()
