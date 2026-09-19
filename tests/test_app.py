import unittest
from unittest.mock import patch

import mysql.connector

from app import app


class ApplicationTests(unittest.TestCase):
    def test_database_failure_has_useful_message_and_no_details(self):
        with patch("app.get_dashboard", side_effect=mysql.connector.Error("detail-must-stay-private")):
            response = app.test_client().get("/")
        self.assertEqual(response.status_code, 503)
        self.assertIn("Não foi possível conectar ao MySQL", response.get_data(as_text=True))
        self.assertNotIn("detail-must-stay-private", response.get_data(as_text=True))

    def test_static_assets_are_served(self):
        for path in ("css/style.css", "js/main.js", "images/fluxopag-logo.png"):
            with self.subTest(path=path):
                response = app.test_client().get(f"/static/{path}")
                self.assertEqual(response.status_code, 200)
                response.close()

    def test_all_templates_compile(self):
        for name in app.jinja_env.list_templates():
            with self.subTest(template=name):
                app.jinja_env.get_template(name)
