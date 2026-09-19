import ast
import struct
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class StructureTests(unittest.TestCase):
    def test_required_project_files_exist(self):
        required_files = [
            "app.py",
            "database.py",
            "services.py",
            "utils.py",
            "database/schema.sql",
            "static/css/style.css",
            "static/js/main.js",
            "templates/base.html",
            "templates/dashboard.html",
            "templates/products.html",
            "templates/orders.html",
            "templates/order_details.html",
            "templates/payment.html",
            "templates/history.html",
            "templates/reports.html",
            "templates/account.html",
        ]
        for relative_path in required_files:
            with self.subTest(path=relative_path):
                self.assertTrue((PROJECT_ROOT / relative_path).is_file())

    def test_python_files_have_valid_syntax(self):
        for path in PROJECT_ROOT.glob("*.py"):
            with self.subTest(path=path.name):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_forbidden_frontend_files_do_not_exist(self):
        forbidden_suffixes = {".jsx", ".tsx", ".ts", ".vue", ".svelte"}
        forbidden_names = {"package.json", "package-lock.json", "vite.config.js"}
        found = []
        for path in PROJECT_ROOT.rglob("*"):
            if any(part in {".git", ".venv", "venv", "__pycache__"} for part in path.parts):
                continue
            if path.is_file() and (path.suffix in forbidden_suffixes or path.name in forbidden_names):
                found.append(str(path.relative_to(PROJECT_ROOT)))
        self.assertEqual(found, [])

    def test_requirements_only_contains_python_backend_dependencies(self):
        lines = [
            line.strip().lower()
            for line in (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        ]
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[0].startswith("flask"))
        self.assertTrue(lines[1].startswith("mysql-connector-python"))
        self.assertTrue(lines[2].startswith("python-dotenv"))

    def test_schema_contains_expected_tables_and_rules(self):
        sql = (PROJECT_ROOT / "database/schema.sql").read_text(encoding="utf-8").lower()
        expected_tables = {
            "establishments",
            "categories",
            "products",
            "command_cards",
            "daily_operations",
            "orders",
            "order_items",
            "sales",
            "audit_logs",
        }
        for table in expected_tables:
            with self.subTest(table=table):
                self.assertIn(f"create table if not exists {table}", sql)
        self.assertIn("check (card_number regexp '^[0-9]{4}$')", sql)
        self.assertIn("unique (open_card_id)", sql)
        self.assertIn("unique (order_id)", sql)

    def test_theme_is_saved_and_dark_palette_exists(self):
        javascript = (PROJECT_ROOT / "static/js/main.js").read_text(encoding="utf-8")
        stylesheet = (PROJECT_ROOT / "static/css/style.css").read_text(encoding="utf-8")
        self.assertIn('localStorage.setItem("fluxopag-theme"', javascript)
        self.assertIn('html[data-theme="dark"]', stylesheet)

    def test_supplied_image_dimensions(self):
        expected_images = {
            "static/images/fluxopag-brand-source.png": (397, 180),
            "static/images/fluxopag-logo.png": (42, 44),
            "static/images/menu-icons/dashboard-active.png": (16, 16),
            "static/images/menu-icons/products-active.png": (18, 18),
            "static/images/menu-icons/orders-active.png": (18, 18),
            "static/images/menu-icons/history-active.png": (18, 18),
        }
        for relative_path, expected_size in expected_images.items():
            with self.subTest(path=relative_path):
                path = PROJECT_ROOT / relative_path
                with path.open("rb") as image_file:
                    header = image_file.read(24)
                self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(struct.unpack(">II", header[16:24]), expected_size)


if __name__ == "__main__":
    unittest.main()
