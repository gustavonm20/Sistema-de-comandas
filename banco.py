import mysql.connector
from flask import current_app, g


def obter_banco():
    if "banco" not in g:
        g.banco = mysql.connector.connect(
            host=current_app.config["MYSQL_SERVIDOR"],
            port=current_app.config["MYSQL_PORTA"],
            user=current_app.config["MYSQL_USUARIO"],
            password=current_app.config["MYSQL_SENHA"],
            database=current_app.config["MYSQL_BANCO"],
            charset="utf8mb4",
            autocommit=True,
            connection_timeout=5,
        )
    return g.banco


def fechar_banco(_erro=None):
    banco = g.pop("banco", None)
    if banco is not None and banco.is_connected():
        banco.close()


def buscar_todos(consulta, parametros=()):
    banco = obter_banco()
    cursor = banco.cursor(dictionary=True)
    try:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()
    finally:
        cursor.close()


def buscar_um(consulta, parametros=()):
    banco = obter_banco()
    cursor = banco.cursor(dictionary=True)
    try:
        cursor.execute(consulta, parametros)
        return cursor.fetchone()
    finally:
        cursor.close()
