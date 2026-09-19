import unittest
from unittest.mock import patch

from services import ServiceError, create_command_card, list_sales, validate_product


class ValidationTests(unittest.TestCase):
    def test_invalid_product_is_rejected_before_database_access(self):
        with patch("services.fetch_one") as query:
            for name, price in (("A", "5"), ("A" * 101, "5"), ("Café", "0"),
                                ("Café", "-1"), ("Café", "NaN"), ("Café", "Infinity")):
                with self.subTest(name=name, price=price), self.assertRaises(ServiceError):
                    validate_product(name, price, "1")
            query.assert_not_called()

    def test_card_requires_four_ascii_digits(self):
        with patch("services.execute_with_audit") as write:
            for number in ("123", "12345", "ABCD", "１２３４", "١٢٣٤"):
                with self.subTest(number=number), self.assertRaises(ServiceError):
                    create_command_card(number)
            write.assert_not_called()

    def test_invalid_history_dates_do_not_reach_database(self):
        with patch("services.fetch_all") as query:
            for start, end in (("2026-02-30", ""), ("", "invalid"), ("2026-09-02", "2026-09-01")):
                with self.subTest(start=start, end=end), self.assertRaises(ServiceError):
                    list_sales(date_from=start, date_to=end)
            query.assert_not_called()
