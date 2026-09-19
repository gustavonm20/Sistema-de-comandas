"""Testes reais: exigem EXECUTAR_TESTES_MYSQL=1 e um banco fluxopag_teste_* descartável."""

import os
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import mysql.connector

from aplicacao import aplicacao
from banco import buscar_todos, buscar_um, obter_banco
import servicos


@unittest.skipUnless(os.getenv("EXECUTAR_TESTES_MYSQL") == "1", "MySQL isolado não solicitado")
class TestesIntegracaoMySQL(unittest.TestCase):
    def setUp(instancia):
        if not aplicacao.config["MYSQL_BANCO"].startswith("fluxopag_teste_"):
            raise RuntimeError("Os testes só podem limpar bancos com prefixo fluxopag_teste_.")
        configuracao = patch.dict(aplicacao.config, TESTING=True)
        configuracao.start()
        instancia.addCleanup(configuracao.stop)
        instancia.contexto = aplicacao.app_context()
        instancia.contexto.push()
        instancia.addCleanup(instancia.contexto.pop)
        conexao = obter_banco()
        cursor = conexao.cursor()
        try:
            for tabela in ("registros_auditoria", "vendas", "itens_pedido", "pedidos", "operacoes_diarias", "produtos"):
                cursor.execute(f"DELETE FROM {tabela}")
        finally:
            cursor.close()
        instancia.id_categoria = buscar_um("SELECT id_categoria FROM categorias WHERE nome = 'Bebidas'")["id_categoria"]
        instancia.id_cartao = buscar_um("SELECT id_cartao FROM cartoes_comanda WHERE numero_cartao = '0001'")["id_cartao"]
        instancia.id_produto = servicos.criar_produto("Café fictício", "5,00", instancia.id_categoria)

    def abrir_pedido(instancia):
        servicos.abrir_operacao("100,00")
        return servicos.criar_pedido(instancia.id_cartao, "balcao")

    def teste_catalogo_filtros_edicao_situacao_e_reconexao(instancia):
        instancia.assertEqual(len(servicos.listar_produtos("café", instancia.id_categoria, "ativo")), 1)
        servicos.atualizar_produto(instancia.id_produto, "Café especial", "6,50", instancia.id_categoria)
        servicos.alterar_situacao_produto(instancia.id_produto, False)
        instancia.assertEqual(servicos.listar_produtos(situacao="ativo"), [])
        instancia.assertEqual(len(servicos.listar_produtos(situacao="inativo")), 1)
        servicos.alterar_situacao_produto(instancia.id_produto, True)
        # Outra conexão comprova persistência fora da conexão que escreveu.
        from banco import fechar_banco
        fechar_banco()
        instancia.assertEqual(servicos.obter_produto(instancia.id_produto)["preco"], Decimal("6.50"))

    def teste_unicidade_cartao_operacao(instancia):
        instancia.abrir_pedido()
        with instancia.assertRaises(servicos.ErroServico):
            servicos.criar_pedido(instancia.id_cartao, "balcao")
        with instancia.assertRaises(servicos.ErroServico):
            servicos.abrir_operacao("0")

    def teste_operacao_obrigatoria_antes_pedido(instancia):
        with instancia.assertRaises(servicos.ErroServico):
            servicos.criar_pedido(instancia.id_cartao, "balcao")

    def teste_produtos_inativos_e_precos_historicos(instancia):
        id_pedido = instancia.abrir_pedido()
        servicos.adicionar_item_pedido(id_pedido, instancia.id_produto, 2)
        servicos.atualizar_produto(instancia.id_produto, "Novo nome", "9,00", instancia.id_categoria)
        servicos.alterar_situacao_produto(instancia.id_produto, False)
        with instancia.assertRaises(servicos.ErroServico):
            servicos.adicionar_item_pedido(id_pedido, instancia.id_produto, 1)
        id_venda = servicos.fechar_pedido(id_pedido, "pix")
        venda = servicos.obter_venda(id_venda)
        instancia.assertEqual(venda["valor_total"], Decimal("10.00"))
        instancia.assertEqual(venda["itens"][0]["nome_produto_historico"], "Café fictício")
        instancia.assertEqual(buscar_um("SELECT nome_produto FROM visao_resumo_pedidos WHERE id_pedido = %s", (id_pedido,))["nome_produto"], "Café fictício")

    def teste_pagamento_libera_cartao_e_impede_segunda_venda(instancia):
        id_pedido = instancia.abrir_pedido()
        servicos.adicionar_item_pedido(id_pedido, instancia.id_produto, 2)
        id_venda = servicos.fechar_pedido(id_pedido, "dinheiro", "20")
        instancia.assertEqual(servicos.obter_venda(id_venda)["troco"], Decimal("10.00"))
        instancia.assertEqual(servicos.obter_pedido(id_pedido)["situacao"], "fechado")
        for acao in (lambda: servicos.fechar_pedido(id_pedido, "pix"),
                       lambda: servicos.adicionar_item_pedido(id_pedido, instancia.id_produto, 1)):
            with instancia.assertRaises(servicos.ErroServico):
                acao()
        instancia.assertNotEqual(servicos.criar_pedido(instancia.id_cartao, "balcao"), id_pedido)

    def teste_pagamento_revertido_quando_auditoria_falha(instancia):
        id_pedido = instancia.abrir_pedido()
        servicos.adicionar_item_pedido(id_pedido, instancia.id_produto, 1)
        with patch("servicos.registrar_auditoria", side_effect=RuntimeError("Falha simulada após gravar a venda")):
            with instancia.assertRaises(RuntimeError):
                servicos.fechar_pedido(id_pedido, "pix")
        instancia.assertEqual(servicos.obter_pedido(id_pedido)["situacao"], "aberto")
        instancia.assertEqual(buscar_um("SELECT COUNT(*) AS total FROM vendas")["total"], 0)

    def teste_pedido_vazio_e_dinheiro_insuficiente(instancia):
        id_pedido = instancia.abrir_pedido()
        with instancia.assertRaises(servicos.ErroServico):
            servicos.fechar_pedido(id_pedido, "pix")
        servicos.adicionar_item_pedido(id_pedido, instancia.id_produto, 1)
        with instancia.assertRaises(servicos.ErroServico):
            servicos.fechar_pedido(id_pedido, "dinheiro", "4,99")
        instancia.assertEqual(servicos.obter_pedido(id_pedido)["situacao"], "aberto")

    def teste_atualizacao_remocao_itens_e_limite_quantidade(instancia):
        id_pedido = instancia.abrir_pedido()
        servicos.adicionar_item_pedido(id_pedido, instancia.id_produto, 99)
        with instancia.assertRaises(servicos.ErroServico):
            servicos.adicionar_item_pedido(id_pedido, instancia.id_produto, 1)
        id_item = servicos.obter_pedido(id_pedido)["itens"][0]["id_item"]
        servicos.atualizar_item_pedido(id_pedido, id_item, 99)
        servicos.atualizar_item_pedido(id_pedido, id_item, 2)
        instancia.assertEqual(servicos.obter_pedido(id_pedido)["total"], Decimal("10.00"))
        servicos.remover_item_pedido(id_pedido, id_item)
        instancia.assertEqual(servicos.obter_pedido(id_pedido)["itens"], [])

    def teste_conferencia_caixa_e_bloqueio_pedido_aberto(instancia):
        id_pedido = instancia.abrir_pedido()
        with instancia.assertRaises(servicos.ErroServico):
            servicos.fechar_operacao("100", "")
        servicos.adicionar_item_pedido(id_pedido, instancia.id_produto, 1)
        servicos.fechar_pedido(id_pedido, "dinheiro", "10")
        segundo = servicos.criar_pedido(instancia.id_cartao, "balcao")
        servicos.adicionar_item_pedido(segundo, instancia.id_produto, 1)
        servicos.fechar_pedido(segundo, "pix")
        instancia.assertEqual(servicos.obter_operacao_aberta()["caixa_esperado_atual"], Decimal("105.00"))
        with instancia.assertRaises(servicos.ErroServico):
            servicos.fechar_operacao("104", "")
        servicos.fechar_operacao("104", "Diferença fictícia de contagem")
        registro = buscar_um("SELECT * FROM operacoes_diarias ORDER BY id_operacao DESC LIMIT 1")
        instancia.assertEqual(registro["valor_diferenca"], Decimal("-1.00"))
        instancia.assertIsNone(servicos.obter_operacao_aberta())

    def teste_restricoes_sql_e_visoes(instancia):
        cursor = obter_banco().cursor()
        try:
            with instancia.assertRaises(mysql.connector.Error):
                cursor.execute("INSERT INTO cartoes_comanda (numero_cartao) VALUES ('ABCD')")
            with instancia.assertRaises(mysql.connector.Error):
                cursor.execute("UPDATE produtos SET preco = -1 WHERE id_produto = %s", (instancia.id_produto,))
            with instancia.assertRaises(mysql.connector.Error):
                cursor.execute("UPDATE produtos SET id_categoria = -1 WHERE id_produto = %s", (instancia.id_produto,))
        finally:
            cursor.close()
        for visao in ("visao_produtos", "visao_pedidos_abertos", "visao_resumo_pedidos", "visao_historico_vendas",
                     "visao_resumo_diario", "visao_resumo_semanal", "visao_resumo_mensal"):
            buscar_todos(f"SELECT * FROM {visao}")

    def teste_protecao_inicializacao_e_reexecucao_estrutura(instancia):
        from inicializar_banco import inicializar_banco
        with instancia.assertRaisesRegex(ValueError, "já contém tabelas"):
            inicializar_banco()
        sql = Path("banco_dados/estrutura.sql").read_text(encoding="utf-8")
        sql = sql.replace("comandas", aplicacao.config["MYSQL_BANCO"])
        cursor = obter_banco().cursor()
        try:
            for comando in sql.split(";"):
                if comando.strip():
                    cursor.execute(comando)
        finally:
            cursor.close()
        instancia.assertEqual(servicos.obter_produto(instancia.id_produto)["nome"], "Café fictício")

    def teste_resumos_e_paginas_com_banco_real(instancia):
        id_pedido = instancia.abrir_pedido()
        servicos.adicionar_item_pedido(id_pedido, instancia.id_produto, 1)
        id_venda = servicos.fechar_pedido(id_pedido, "pix")
        for periodo in ("diario", "semanal", "mensal"):
            resumo = servicos.obter_resumo(periodo)
            instancia.assertEqual(resumo["indicadores"]["faturamento"], Decimal("5.00"))
            if periodo != "diario":
                instancia.assertRegex(resumo["evolucao"][0]["rotulo"], r"^\d{2}/\d{2}$")
        cliente = aplicacao.test_client()
        for caminho in ("/", "/produtos", "/produtos/novo", f"/produtos/{instancia.id_produto}/editar",
                     "/cartoes", "/pedidos", "/pedidos/novo", f"/pedidos/{id_pedido}",
                     f"/pedidos/{id_pedido}/pagamento", "/historico", f"/vendas/{id_venda}",
                     "/resumos?periodo=diario", "/resumos?periodo=semanal", "/resumos?periodo=mensal", "/conta"):
            with instancia.subTest(caminho=caminho):
                instancia.assertEqual(cliente.get(caminho).status_code, 200)

    def teste_formularios_em_portugues_com_fluxo_completo(instancia):
        cliente = aplicacao.test_client()
        def enviar_formulario(caminho, **parametros):
            resposta = cliente.post(caminho, **parametros)
            instancia.assertEqual(resposta.status_code, 302)
            return resposta
        resposta = enviar_formulario("/produtos/novo", data={"nome": "Bolo fictício", "preco": "8,50", "id_categoria": instancia.id_categoria})
        instancia.assertEqual(resposta.status_code, 302)
        bolo = buscar_um("SELECT id_produto FROM produtos WHERE nome = 'Bolo fictício'")["id_produto"]
        enviar_formulario(f"/produtos/{bolo}/editar", data={"nome": "Bolo revisado", "preco": "9,00", "id_categoria": instancia.id_categoria})
        enviar_formulario("/operacao/abrir", data={"caixa_inicial": "100,00"})
        enviar_formulario("/pedidos/novo", data={"id_cartao": instancia.id_cartao, "tipo_atendimento": "mesa", "identificacao_atendimento": "4", "observacao": "Pedido fictício"})
        pedido = buscar_um("SELECT id_pedido FROM pedidos WHERE situacao = 'aberto'")["id_pedido"]
        enviar_formulario(f"/pedidos/{pedido}/itens", data={"id_produto": bolo, "quantidade": "2"})
        item = servicos.obter_pedido(pedido)["itens"][0]["id_item"]
        enviar_formulario(f"/pedidos/{pedido}/itens/{item}/quantidade", data={"quantidade": "3"})
        instancia.assertEqual(servicos.obter_pedido(pedido)["total"], Decimal("27.00"))
        resposta = cliente.get(f"/pedidos/{pedido}/pagamento")
        instancia.assertEqual(resposta.status_code, 200)
        instancia.assertIn('name="forma_pagamento"', resposta.get_data(as_text=True))
        enviar_formulario(f"/pedidos/{pedido}/pagamento", data={"forma_pagamento": "dinheiro", "valor_recebido": "30,00"})
        venda = buscar_um("SELECT * FROM vendas WHERE id_pedido = %s", (pedido,))
        instancia.assertEqual(venda["troco"], Decimal("3.00"))
        enviar_formulario(f"/produtos/{bolo}/situacao", data={"ativo": "false"})
        instancia.assertFalse(servicos.obter_produto(bolo)["ativo"])
        enviar_formulario("/operacao/fechar", data={"caixa_contado": "127,00", "justificativa_diferenca": ""})
        instancia.assertIsNone(servicos.obter_operacao_aberta())
