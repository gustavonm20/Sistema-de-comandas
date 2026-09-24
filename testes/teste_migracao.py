"""Cópia da estrutura anterior, com bancos descartáveis e comparação independente."""
import os
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from aplicacao import aplicacao
from banco import obter_banco, buscar_um, fechar_banco
from migrar_banco import migrar_banco
import mysql.connector


@unittest.skipUnless(os.getenv("EXECUTAR_TESTES_MYSQL") == "1", "MySQL isolado não solicitado")
class TestesMigracao(unittest.TestCase):
    def setUp(instancia):
        base = aplicacao.config["MYSQL_BANCO"]
        if not base.startswith("fluxopag_teste_"):
            raise RuntimeError("Use um banco descartável com prefixo fluxopag_teste_.")
        instancia.origem = base + "_origem"
        instancia.destino = base + "_destino"
        instancia.conexao = mysql.connector.connect(
            host=aplicacao.config["MYSQL_SERVIDOR"], port=aplicacao.config["MYSQL_PORTA"],
            user=aplicacao.config["MYSQL_USUARIO"], password=aplicacao.config["MYSQL_SENHA"], autocommit=True,
        )
        instancia.addCleanup(instancia.conexao.close)
        instancia.cursor = instancia.conexao.cursor()
        instancia.addCleanup(instancia.cursor.close)
        instancia.addCleanup(instancia.limpar_bancos)
        instancia.limpar_bancos()
        # Referência imutável: estrutura publicada antes da tradução.
        referencia = (
            Path(__file__).resolve().parents[1]
            / "banco_dados"
            / "legado"
            / "estrutura_flask_anterior.sql"
        )
        estrutura = referencia.read_text(encoding="utf-8")
        for comando in estrutura.replace("comandas_db", instancia.origem).split(";"):
            if comando.strip():
                instancia.cursor.execute(comando)
        # Grafias originais são necessárias para testar a leitura de bancos antigos.
        for comando in [
            "INSERT INTO products (product_id, name, normalized_name, price, category_id) VALUES (31, 'Café novo', 'café novo', 9.90, 1)",
            "INSERT INTO daily_operations (operation_id, opening_cash) VALUES (12, 100.00)",
            "INSERT INTO orders (order_id, card_id, operation_id, status, closed_at, service_type) VALUES (42, 1, 12, 'closed', '2026-09-18 12:15:00', 'table')",
            "INSERT INTO order_items (order_id, product_id, product_name_snapshot, category_name_snapshot, unit_price, quantity) VALUES (42, 31, 'Café original', 'Bebidas', 5.50, 2)",
            "INSERT INTO sales (sale_id, order_id, card_number_snapshot, total_amount, payment_method, cash_received, change_amount) VALUES (81, 42, '0001', 11.00, 'cash', 20.00, 9.00)",
            "INSERT INTO audit_logs (actor, action, entity_type, entity_id, detail) VALUES ('local-admin', 'order.closed', 'order', 42, 'Observação preservada')",
            "INSERT INTO orders (order_id, card_id, operation_id, service_type) VALUES (43, 2, 12, 'counter')",
        ]:
            instancia.cursor.execute(comando)

    def limpar_bancos(instancia):
        for nome in (instancia.origem, instancia.destino):
            if not nome.startswith("fluxopag_teste_") or not all(c.isalnum() or c == '_' for c in nome):
                raise RuntimeError("Nome de banco de teste inválido.")
            instancia.cursor.execute(f"DROP DATABASE IF EXISTS `{nome}`")

    def teste_copia_valores_historicos_e_mantem_origem(instancia):
        contagens = migrar_banco(instancia.origem, instancia.destino)
        instancia.assertEqual(contagens["pedidos"], 2)
        instancia.cursor.execute(f"SELECT total_amount, payment_method FROM `{instancia.origem}`.sales WHERE sale_id = 81")
        instancia.assertEqual(instancia.cursor.fetchone(), (Decimal("11.00"), "cash"))
        with patch.dict(aplicacao.config, MYSQL_BANCO=instancia.destino), aplicacao.app_context():
            from servicos import obter_venda, obter_pedido
            venda = obter_venda(81)
            instancia.assertEqual(venda["troco"], Decimal("9.00"))
            instancia.assertEqual(venda["forma_pagamento"], "dinheiro")
            instancia.assertEqual(venda["itens"][0]["nome_produto_historico"], "Café original")
            instancia.assertEqual(venda["itens"][0]["preco_unitario"], Decimal("5.50"))
            instancia.assertEqual(obter_pedido(43)["situacao"], "aberto")
            registro = buscar_um("SELECT * FROM registros_auditoria")
            instancia.assertEqual(registro["acao"], "pedido.fechado")
            instancia.assertEqual(registro["detalhe"], "Observação preservada")
            fechar_banco()

    def teste_recusa_destino_ocupado_e_mesmo_banco(instancia):
        with instancia.assertRaisesRegex(ValueError, "diferentes"):
            migrar_banco(instancia.origem, instancia.origem)
        migrar_banco(instancia.origem, instancia.destino)
        with instancia.assertRaisesRegex(ValueError, "já contém tabelas"):
            migrar_banco(instancia.origem, instancia.destino)

    def teste_falha_reverte_copia_sem_alterar_origem(instancia):
        from compatibilidade import converter_valor_antigo
        def simular_erro(coluna, valor):
            return -1 if coluna == "preco_unitario" else converter_valor_antigo(coluna, valor)
        with patch("migrar_banco.converter_valor_antigo", side_effect=simular_erro):
            with instancia.assertRaises(mysql.connector.Error):
                migrar_banco(instancia.origem, instancia.destino)
        instancia.cursor.execute(f"SELECT COUNT(*) FROM `{instancia.destino}`.produtos")
        instancia.assertEqual(instancia.cursor.fetchone()[0], 0)
        instancia.cursor.execute(f"SELECT COUNT(*) FROM `{instancia.origem}`.products")
        instancia.assertEqual(instancia.cursor.fetchone()[0], 1)

    def teste_recusa_estrutura_antiga_incompleta(instancia):
        instancia.cursor.execute(f"DROP TABLE `{instancia.origem}`.audit_logs")
        with instancia.assertRaisesRegex(ValueError, "nove tabelas"):
            migrar_banco(instancia.origem, instancia.destino)
        instancia.cursor.execute("SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = %s", (instancia.destino,))
        instancia.assertEqual(instancia.cursor.fetchone()[0], 0)
