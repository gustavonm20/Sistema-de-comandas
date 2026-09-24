import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path

from servicos import ErroNegocio, ServicoComandas


class TestesServicoComandas(unittest.TestCase):
    def setUp(instancia) -> None:
        instancia.diretorio_temporario = tempfile.TemporaryDirectory()
        instancia.servico = ServicoComandas(Path(instancia.diretorio_temporario.name) / "banco.json")

    def tearDown(instancia) -> None:
        instancia.diretorio_temporario.cleanup()

    def teste_venda_completa_libera_comanda(instancia) -> None:
        produto = instancia.servico.adicionar_produto("Café", 500, "Bebidas")
        instancia.servico.abrir_caixa(10000)
        instancia.servico.abrir_pedido(1)
        instancia.servico.adicionar_item(1, produto.id_produto, 2)
        venda = instancia.servico.fechar_pedido(1, "1")
        instancia.assertEqual(venda.total_centavos, 1000)
        instancia.assertEqual(instancia.servico.pedidos, [])
        instancia.servico.abrir_pedido(1)

    def teste_fechamento_caixa_bloqueado_com_pedido_aberto(instancia) -> None:
        instancia.servico.abrir_caixa(0)
        instancia.servico.abrir_pedido(4)
        with instancia.assertRaises(ErroNegocio):
            instancia.servico.fechar_caixa(0)

    def teste_diferenca_caixa_considera_apenas_dinheiro(instancia) -> None:
        produto = instancia.servico.adicionar_produto("Pão", 200, "Padaria")
        instancia.servico.abrir_caixa(5000)
        for numero, pagamento in [(1, "1"), (2, "2")]:
            instancia.servico.abrir_pedido(numero)
            instancia.servico.adicionar_item(numero, produto.id_produto, 5)
            instancia.servico.fechar_pedido(numero, pagamento)
        sessao = instancia.servico.fechar_caixa(5900)
        instancia.assertEqual(sessao.caixa_esperado_centavos, 6000)
        instancia.assertEqual(sessao.diferenca_centavos, -100)

    def teste_produto_desativado_nao_pode_ser_vendido(instancia) -> None:
        produto = instancia.servico.adicionar_produto("Suco", 800, "Bebidas")
        instancia.servico.desativar_produto(produto.id_produto)
        instancia.servico.abrir_caixa(0)
        instancia.servico.abrir_pedido(1)
        with instancia.assertRaises(ErroNegocio):
            instancia.servico.adicionar_item(1, produto.id_produto, 1)

    def teste_resumo_diario(instancia) -> None:
        produto = instancia.servico.adicionar_produto("Bolo", 1200, "Confeitaria")
        instancia.servico.abrir_caixa(0)
        instancia.servico.abrir_pedido(1)
        instancia.servico.adicionar_item(1, produto.id_produto, 2)
        instancia.servico.fechar_pedido(1, "2")
        resumo = instancia.servico.resumo_periodo("dia", date.today())
        instancia.assertEqual(resumo["quantidade_vendas"], 1)
        instancia.assertEqual(resumo["total_centavos"], 2400)
        instancia.assertEqual(resumo["produtos_mais_vendidos"], [("Bolo", 2)])

    def teste_persistencia(instancia) -> None:
        instancia.servico.adicionar_produto("Coxinha", 750, "Salgados")
        recarregado = ServicoComandas(instancia.servico.armazenamento.caminho_arquivo)
        instancia.assertEqual(recarregado.produtos[0].nome, "Coxinha")

    def teste_carrega_formato_antigo_sem_sobrescrever(instancia):
        import json
        raiz = Path(instancia.diretorio_temporario.name)
        anterior = raiz / "data" / "database.json"
        anterior.parent.mkdir()
        # Chaves do contrato antigo são mantidas somente neste cenário de compatibilidade.
        conteudo = json.dumps({"products": [{"product_id": 8, "name": "Café antigo", "price_cents": 550, "category": "Bebidas", "active": True}], "open_orders": [], "sales": [], "cash_sessions": []})
        anterior.write_text(conteudo)
        destino = raiz / "dados" / "banco.json"
        servico = ServicoComandas(destino)
        instancia.assertEqual(servico.produtos[0].preco_centavos, 550)
        servico.adicionar_produto("Bolo", 900, "Sobremesas")
        instancia.assertEqual(anterior.read_text(), conteudo)
        instancia.assertEqual(len(json.loads(destino.read_text())["produtos"]), 2)

    def teste_recusa_chaves_antigas_e_novas_duplicadas(instancia):
        from compatibilidade import converter_dados_antigos
        with instancia.assertRaisesRegex(ValueError, "mistura chaves"):
            converter_dados_antigos({"products": [], "produtos": []})


if __name__ == "__main__":
    unittest.main()
