"""Inicializa somente um banco vazio; nunca apaga nem migra dados existentes."""

import argparse
import getpass
import re
from pathlib import Path

import mysql.connector

from app import app


def initialize_database(user=None, password=None):
    database_name = app.config["MYSQL_DATABASE"]
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", database_name):
        raise ValueError("Use apenas letras, números e sublinhado no nome do banco.")
    connection = mysql.connector.connect(
        host=app.config["MYSQL_HOST"], port=app.config["MYSQL_PORT"],
        user=user or app.config["MYSQL_USER"],
        password=app.config["MYSQL_PASSWORD"] if password is None else password,
        autocommit=True, connection_timeout=5,
    )
    cursor = connection.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s",
            (database_name,),
        )
        if cursor.fetchone()[0]:
            raise ValueError(
                "O banco já contém tabelas. Nenhuma alteração foi feita. "
                "Escolha um banco vazio ou consulte docs/DATABASE.md e a issue #19."
            )
        sql = Path(__file__).with_name("database").joinpath("schema.sql").read_text(encoding="utf-8")
        sql = sql.replace("comandas_db", database_name)
        # O schema não contém procedures nem delimitadores personalizados.
        for statement in sql.split(";"):
            if statement.strip():
                cursor.execute(statement)
        print(f"Banco {database_name} inicializado. Tabelas, views e dados básicos criados.")
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", help="Usuário MySQL autorizado a criar a estrutura")
    parser.add_argument("--ask-password", action="store_true", help="Solicitar senha sem exibi-la")
    args = parser.parse_args()
    password = getpass.getpass("Senha do MySQL: ") if args.ask_password else None
    try:
        initialize_database(args.user, password)
    except (ValueError, mysql.connector.Error) as error:
        parser.exit(1, f"Não foi possível inicializar: {error}\n")
