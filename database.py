import mysql.connector
from flask import current_app, g


def get_database():
    if "database" not in g:
        g.database = mysql.connector.connect(
            host=current_app.config["MYSQL_HOST"],
            port=current_app.config["MYSQL_PORT"],
            user=current_app.config["MYSQL_USER"],
            password=current_app.config["MYSQL_PASSWORD"],
            database=current_app.config["MYSQL_DATABASE"],
            charset="utf8mb4",
            autocommit=True,
            connection_timeout=5,
        )
    return g.database


def close_database(_error=None):
    database = g.pop("database", None)
    if database is not None and database.is_connected():
        database.close()


def fetch_all(query, parameters=()):
    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        cursor.execute(query, parameters)
        return cursor.fetchall()
    finally:
        cursor.close()


def fetch_one(query, parameters=()):
    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        cursor.execute(query, parameters)
        return cursor.fetchone()
    finally:
        cursor.close()
