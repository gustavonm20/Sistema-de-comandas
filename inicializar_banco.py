"""Inicializa somente um banco vazio; nunca apaga nem migra dados existentes."""

import argparse
import getpass
import re
from pathlib import Path

import mysql.connector

from aplicacao import aplicacao


def inicializar_banco(usuario=None, senha=None, nome_banco=None, incluir_dados_iniciais=True):
    nome_banco = nome_banco or aplicacao.config["MYSQL_BANCO"]
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", nome_banco):
        raise ValueError("Use apenas letras, números e sublinhado no nome do banco.")
    conexao = mysql.connector.connect(
        host=aplicacao.config["MYSQL_SERVIDOR"], port=aplicacao.config["MYSQL_PORTA"],
        user=usuario or aplicacao.config["MYSQL_USUARIO"],
        password=aplicacao.config["MYSQL_SENHA"] if senha is None else senha,
        autocommit=True, connection_timeout=5,
    )
    cursor = conexao.cursor()
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s",
            (nome_banco,),
        )
        if cursor.fetchone()[0]:
            raise ValueError(
                "O banco já contém tabelas. Nenhuma alteração foi feita. "
                "Escolha um banco vazio ou consulte documentacao/BANCO_DADOS.md e a tarefa #19."
            )
        sql = Path(__file__).with_name("banco_dados").joinpath("estrutura.sql").read_text(encoding="utf-8")
        sql = sql.replace("comandas", nome_banco)
        # A estrutura não contém procedimentos nem delimitadores personalizados.
        for comando in sql.split(";"):
            sem_comentarios = re.sub(r"--[^\n]*", "", comando).strip()
            if not incluir_dados_iniciais and sem_comentarios.upper().startswith("INSERT"):
                continue
            if comando.strip():
                cursor.execute(comando)
        print(f"Banco {nome_banco} inicializado. Estrutura criada.")
    finally:
        cursor.close()
        conexao.close()


if __name__ == "__main__":
    analisador = argparse.ArgumentParser(description=__doc__)
    analisador.add_argument("--usuario", help="Usuário MySQL autorizado a criar a estrutura")
    analisador.add_argument("--solicitar-senha", action="store_true", help="Solicitar senha sem exibi-la")
    argumentos = analisador.parse_args()
    senha = getpass.getpass("Senha do MySQL: ") if argumentos.solicitar_senha else None
    try:
        inicializar_banco(argumentos.usuario, senha)
    except (ValueError, mysql.connector.Error) as erro:
        analisador.exit(1, f"Não foi possível inicializar: {erro}\n")
