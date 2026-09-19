"""Copia o MySQL antigo para um banco novo com nomes em português, sem alterar a origem."""

import argparse
import getpass
import re

import mysql.connector

from aplicacao import aplicacao
from compatibilidade import TABELAS_ANTIGAS, converter_valor_antigo
from inicializar_banco import inicializar_banco


def migrar_banco(origem, destino, usuario=None, senha=None):
    for nome in (origem, destino):
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", nome):
            raise ValueError("Use apenas letras, números e sublinhado nos nomes dos bancos.")
    if origem.casefold() == destino.casefold():
        raise ValueError("Origem e destino precisam ser bancos diferentes.")
    configuracao = {
        "host": aplicacao.config["MYSQL_SERVIDOR"],
        "port": aplicacao.config["MYSQL_PORTA"],
        "user": usuario or aplicacao.config["MYSQL_USUARIO"],
        "password": aplicacao.config["MYSQL_SENHA"] if senha is None else senha,
        "autocommit": True,
        "charset": "utf8mb4",
    }
    leitura = mysql.connector.connect(database=origem, **configuracao)
    escrita = None
    cursor_origem = leitura.cursor(dictionary=True)
    cursor_destino = None
    try:
        cursor_origem.execute(
            "SELECT TABLE_NAME, ENGINE FROM information_schema.tables "
            "WHERE table_schema = %s AND table_type = 'BASE TABLE'", (origem,)
        )
        tabelas = {registro["TABLE_NAME"]: registro["ENGINE"] for registro in cursor_origem.fetchall()}
        if set(tabelas) != {antiga for antiga, _, _, _ in TABELAS_ANTIGAS}:
            raise ValueError("A origem não corresponde à versão Flask anterior de nove tabelas. Consulte a documentação.")
        if any(motor != "InnoDB" for motor in tabelas.values()):
            raise ValueError("A cópia consistente exige tabelas InnoDB na origem.")
        for antiga, _, colunas, geradas in TABELAS_ANTIGAS:
            cursor_origem.execute(
                "SELECT COLUMN_NAME FROM information_schema.columns WHERE table_schema = %s AND table_name = %s",
                (origem, antiga),
            )
            if {registro["COLUMN_NAME"] for registro in cursor_origem.fetchall()} != set(colunas) | set(geradas):
                raise ValueError(f"Estrutura de origem não reconhecida: {antiga}. Nenhum dado foi copiado.")

        # Esta rotina recusa um destino já ocupado e nunca executa SQL de remoção.
        inicializar_banco(usuario, senha, nome_banco=destino, incluir_dados_iniciais=False)
        escrita = mysql.connector.connect(database=destino, **configuracao)
        cursor_destino = escrita.cursor(dictionary=True)
        leitura.start_transaction(consistent_snapshot=True, isolation_level="REPEATABLE READ", readonly=True)
        escrita.start_transaction()
        contagens = {}
        for antiga, nova, colunas, _ in TABELAS_ANTIGAS:
            nomes_antigos = ", ".join(f"`{coluna}`" for coluna in colunas)
            nomes_novos = ", ".join(f"`{coluna}`" for coluna in colunas.values())
            cursor_origem.execute(f"SELECT {nomes_antigos} FROM `{antiga}` ORDER BY `{next(iter(colunas))}`")
            registros = cursor_origem.fetchall()
            convertidos = [
                tuple(converter_valor_antigo(novo, registro[velho]) for velho, novo in colunas.items())
                for registro in registros
            ]
            if convertidos:
                marcadores = ", ".join(["%s"] * len(colunas))
                cursor_destino.executemany(f"INSERT INTO `{nova}` ({nomes_novos}) VALUES ({marcadores})", convertidos)
            # Conferir todos os valores persistidos antes de confirmar a transação.
            cursor_destino.execute(f"SELECT {nomes_novos} FROM `{nova}` ORDER BY `{next(iter(colunas.values()))}`")
            gravados = [tuple(registro[coluna] for coluna in colunas.values()) for registro in cursor_destino.fetchall()]
            if gravados != convertidos:
                raise ValueError(f"A conferência da tabela {nova} falhou. Os dados do destino serão revertidos.")
            contagens[nova] = len(convertidos)
        escrita.commit()
        return contagens
    except Exception:
        if escrita is not None:
            escrita.rollback()
        raise
    finally:
        leitura.rollback()
        cursor_origem.close()
        leitura.close()
        if cursor_destino is not None:
            cursor_destino.close()
        if escrita is not None:
            escrita.close()


if __name__ == "__main__":
    analisador = argparse.ArgumentParser(description=__doc__)
    analisador.add_argument("--origem", required=True, help="Banco da versão anterior")
    analisador.add_argument("--destino", required=True, help="Banco novo e vazio")
    analisador.add_argument("--usuario", help="Usuário autorizado a ler a origem e criar o destino")
    analisador.add_argument("--solicitar-senha", action="store_true", help="Solicitar senha sem exibi-la")
    analisador.add_argument("--operacao-parada", action="store_true", required=True,
                            help="Confirma que as gravações na aplicação antiga foram interrompidas")
    argumentos = analisador.parse_args()
    senha = getpass.getpass("Senha do MySQL: ") if argumentos.solicitar_senha else None
    try:
        contagens = migrar_banco(argumentos.origem, argumentos.destino, argumentos.usuario, senha)
        print("Cópia concluída e conferida. O banco de origem foi preservado.")
        for tabela, quantidade in contagens.items():
            print(f"{tabela}: {quantidade} registro(s)")
        print("Aponte MYSQL_BANCO no .env para o destino após conferir a aplicação.")
    except (ValueError, mysql.connector.Error) as erro:
        analisador.exit(1, f"Não foi possível migrar: {erro}\n")
