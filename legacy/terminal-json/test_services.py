import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path

from services import BusinessError, CommandService


class CommandServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.service = CommandService(Path(self.temp_directory.name) / "database.json")

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_complete_sale_releases_order(self) -> None:
        product = self.service.add_product("Café", 500, "Bebidas")
        self.service.open_cash(10000)
        self.service.open_order(1)
        self.service.add_item(1, product.product_id, 2)
        sale = self.service.close_order(1, "1")
        self.assertEqual(sale.total_cents, 1000)
        self.assertEqual(self.service.orders, [])
        self.service.open_order(1)

    def test_cash_close_is_blocked_with_open_order(self) -> None:
        self.service.open_cash(0)
        self.service.open_order(4)
        with self.assertRaises(BusinessError):
            self.service.close_cash(0)

    def test_cash_difference_uses_only_cash_sales(self) -> None:
        product = self.service.add_product("Pão", 200, "Padaria")
        self.service.open_cash(5000)
        for number, payment in [(1, "1"), (2, "2")]:
            self.service.open_order(number)
            self.service.add_item(number, product.product_id, 5)
            self.service.close_order(number, payment)
        session = self.service.close_cash(5900)
        self.assertEqual(session.expected_cash_cents, 6000)
        self.assertEqual(session.difference_cents, -100)

    def test_deactivated_product_cannot_be_sold(self) -> None:
        product = self.service.add_product("Suco", 800, "Bebidas")
        self.service.deactivate_product(product.product_id)
        self.service.open_cash(0)
        self.service.open_order(1)
        with self.assertRaises(BusinessError):
            self.service.add_item(1, product.product_id, 1)

    def test_daily_summary(self) -> None:
        product = self.service.add_product("Bolo", 1200, "Confeitaria")
        self.service.open_cash(0)
        self.service.open_order(1)
        self.service.add_item(1, product.product_id, 2)
        self.service.close_order(1, "2")
        summary = self.service.period_summary("day", date.today())
        self.assertEqual(summary["sales_count"], 1)
        self.assertEqual(summary["total_cents"], 2400)
        self.assertEqual(summary["top_products"], [("Bolo", 2)])

    def test_persistence(self) -> None:
        self.service.add_product("Coxinha", 750, "Salgados")
        reloaded = CommandService(self.service.storage.file_path)
        self.assertEqual(reloaded.products[0].name, "Coxinha")


if __name__ == "__main__":
    unittest.main()
