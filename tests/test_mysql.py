"""Testes reais: exigem RUN_MYSQL_TESTS=1 e um banco fluxopag_test_* descartável."""

import os
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import mysql.connector

from app import app
from database import fetch_all, fetch_one, get_database
import services


@unittest.skipUnless(os.getenv("RUN_MYSQL_TESTS") == "1", "MySQL isolado não solicitado")
class MySQLIntegrationTests(unittest.TestCase):
    def setUp(self):
        if not app.config["MYSQL_DATABASE"].startswith("fluxopag_test_"):
            raise RuntimeError("Os testes só podem limpar bancos com prefixo fluxopag_test_.")
        self.context = app.app_context()
        self.context.push()
        self.addCleanup(self.context.pop)
        connection = get_database()
        cursor = connection.cursor()
        try:
            for table in ("audit_logs", "sales", "order_items", "orders", "daily_operations", "products"):
                cursor.execute(f"DELETE FROM {table}")
        finally:
            cursor.close()
        self.category_id = fetch_one("SELECT category_id FROM categories WHERE name = 'Bebidas'")["category_id"]
        self.card_id = fetch_one("SELECT card_id FROM command_cards WHERE card_number = '0001'")["card_id"]
        self.product_id = services.create_product("Café fictício", "5,00", self.category_id)

    def open_order(self):
        services.open_operation("100,00")
        return services.create_order(self.card_id, "counter")

    def test_product_catalog_filters_edit_status_and_reconnect(self):
        self.assertEqual(len(services.list_products("café", self.category_id, "active")), 1)
        services.update_product(self.product_id, "Café especial", "6,50", self.category_id)
        services.set_product_status(self.product_id, False)
        self.assertEqual(services.list_products(status="active"), [])
        self.assertEqual(len(services.list_products(status="inactive")), 1)
        services.set_product_status(self.product_id, True)
        # Outra conexão comprova persistência fora da conexão que escreveu.
        from database import close_database
        close_database()
        self.assertEqual(services.get_product(self.product_id)["price"], Decimal("6.50"))

    def test_card_and_operation_uniqueness(self):
        self.open_order()
        with self.assertRaises(services.ServiceError):
            services.create_order(self.card_id, "counter")
        with self.assertRaises(services.ServiceError):
            services.open_operation("0")

    def test_operation_required_before_opening_order(self):
        with self.assertRaises(services.ServiceError):
            services.create_order(self.card_id, "counter")

    def test_inactive_products_and_historical_prices(self):
        order_id = self.open_order()
        services.add_order_item(order_id, self.product_id, 2)
        services.update_product(self.product_id, "Novo nome", "9,00", self.category_id)
        services.set_product_status(self.product_id, False)
        with self.assertRaises(services.ServiceError):
            services.add_order_item(order_id, self.product_id, 1)
        sale_id = services.close_order(order_id, "pix")
        sale = services.get_sale(sale_id)
        self.assertEqual(sale["total_amount"], Decimal("10.00"))
        self.assertEqual(sale["items"][0]["product_name_snapshot"], "Café fictício")
        self.assertEqual(fetch_one("SELECT product_name FROM vw_order_summary WHERE order_id = %s", (order_id,))["product_name"], "Café fictício")

    def test_payment_releases_card_and_prevents_second_sale(self):
        order_id = self.open_order()
        services.add_order_item(order_id, self.product_id, 2)
        sale_id = services.close_order(order_id, "cash", "20")
        self.assertEqual(services.get_sale(sale_id)["change_amount"], Decimal("10.00"))
        self.assertEqual(services.get_order(order_id)["status"], "closed")
        for action in (lambda: services.close_order(order_id, "pix"),
                       lambda: services.add_order_item(order_id, self.product_id, 1)):
            with self.assertRaises(services.ServiceError):
                action()
        self.assertNotEqual(services.create_order(self.card_id, "counter"), order_id)

    def test_payment_rolls_back_when_audit_fails(self):
        order_id = self.open_order()
        services.add_order_item(order_id, self.product_id, 1)
        with patch("services.record_audit", side_effect=RuntimeError("Falha simulada após gravar a venda")):
            with self.assertRaises(RuntimeError):
                services.close_order(order_id, "pix")
        self.assertEqual(services.get_order(order_id)["status"], "open")
        self.assertEqual(fetch_one("SELECT COUNT(*) AS total FROM sales")["total"], 0)

    def test_empty_order_and_insufficient_cash(self):
        order_id = self.open_order()
        with self.assertRaises(services.ServiceError):
            services.close_order(order_id, "pix")
        services.add_order_item(order_id, self.product_id, 1)
        with self.assertRaises(services.ServiceError):
            services.close_order(order_id, "cash", "4,99")
        self.assertEqual(services.get_order(order_id)["status"], "open")

    def test_item_updates_removal_and_quantity_limit(self):
        order_id = self.open_order()
        services.add_order_item(order_id, self.product_id, 99)
        with self.assertRaises(services.ServiceError):
            services.add_order_item(order_id, self.product_id, 1)
        item_id = services.get_order(order_id)["items"][0]["item_id"]
        services.update_order_item(order_id, item_id, 99)
        services.update_order_item(order_id, item_id, 2)
        self.assertEqual(services.get_order(order_id)["total"], Decimal("10.00"))
        services.remove_order_item(order_id, item_id)
        self.assertEqual(services.get_order(order_id)["items"], [])

    def test_cash_reconciliation_and_open_order_block(self):
        order_id = self.open_order()
        with self.assertRaises(services.ServiceError):
            services.close_operation("100", "")
        services.add_order_item(order_id, self.product_id, 1)
        services.close_order(order_id, "cash", "10")
        second = services.create_order(self.card_id, "counter")
        services.add_order_item(second, self.product_id, 1)
        services.close_order(second, "pix")
        self.assertEqual(services.get_open_operation()["expected_cash_live"], Decimal("105.00"))
        with self.assertRaises(services.ServiceError):
            services.close_operation("104", "")
        services.close_operation("104", "Diferença fictícia de contagem")
        row = fetch_one("SELECT * FROM daily_operations ORDER BY operation_id DESC LIMIT 1")
        self.assertEqual(row["difference_amount"], Decimal("-1.00"))
        self.assertIsNone(services.get_open_operation())

    def test_sql_constraints_and_views(self):
        cursor = get_database().cursor()
        try:
            with self.assertRaises(mysql.connector.Error):
                cursor.execute("INSERT INTO command_cards (card_number) VALUES ('ABCD')")
            with self.assertRaises(mysql.connector.Error):
                cursor.execute("UPDATE products SET price = -1 WHERE product_id = %s", (self.product_id,))
            with self.assertRaises(mysql.connector.Error):
                cursor.execute("UPDATE products SET category_id = -1 WHERE product_id = %s", (self.product_id,))
        finally:
            cursor.close()
        for view in ("vw_products", "vw_open_orders", "vw_order_summary", "vw_sales_history",
                     "vw_daily_summary", "vw_weekly_summary", "vw_monthly_summary"):
            fetch_all(f"SELECT * FROM {view}")

    def test_initialization_guard_and_schema_reexecution(self):
        from initialize_database import initialize_database
        with self.assertRaisesRegex(ValueError, "já contém tabelas"):
            initialize_database()
        sql = Path("database/schema.sql").read_text(encoding="utf-8")
        sql = sql.replace("comandas_db", app.config["MYSQL_DATABASE"])
        cursor = get_database().cursor()
        try:
            for statement in sql.split(";"):
                if statement.strip():
                    cursor.execute(statement)
        finally:
            cursor.close()
        self.assertEqual(services.get_product(self.product_id)["name"], "Café fictício")

    def test_reports_and_pages_with_real_database(self):
        order_id = self.open_order()
        services.add_order_item(order_id, self.product_id, 1)
        sale_id = services.close_order(order_id, "pix")
        for period in ("daily", "weekly", "monthly"):
            report = services.get_report(period)
            self.assertEqual(report["metrics"]["revenue"], Decimal("5.00"))
            if period != "daily":
                self.assertRegex(report["trend"][0]["label"], r"^\d{2}/\d{2}$")
        client = app.test_client()
        for path in ("/", "/products", "/products/new", f"/products/{self.product_id}/edit",
                     "/cards", "/orders", "/orders/new", f"/orders/{order_id}",
                     f"/orders/{order_id}/payment", "/history", f"/sales/{sale_id}",
                     "/reports?period=daily", "/reports?period=weekly", "/reports?period=monthly", "/account"):
            with self.subTest(path=path):
                self.assertEqual(client.get(path).status_code, 200)
