import unittest
from unittest.mock import patch

from servicos import ErroServico, criar_cartao_comanda, listar_vendas, validar_produto


class TestesValidacao(unittest.TestCase):
    def teste_produto_invalido_rejeitado_antes_banco(instancia):
        with patch("servicos.buscar_um") as consulta:
            for nome, preco in (("A", "5"), ("A" * 101, "5"), ("Café", "0"),
                                ("Café", "-1"), ("Café", "NaN"), ("Café", "Infinity")):
                with instancia.subTest(nome=nome, preco=preco), instancia.assertRaises(ErroServico):
                    validar_produto(nome, preco, "1")
            consulta.assert_not_called()

    def teste_cartao_exige_quatro_digitos_ascii(instancia):
        with patch("servicos.executar_com_auditoria") as escrever:
            for numero in ("123", "12345", "ABCD", "１２３４", "١٢٣٤"):
                with instancia.subTest(numero=numero), instancia.assertRaises(ErroServico):
                    criar_cartao_comanda(numero)
            escrever.assert_not_called()

    def teste_datas_invalidas_historico_nao_chegam_banco(instancia):
        with patch("servicos.buscar_todos") as consulta:
            for inicio, fim in (("2026-02-30", ""), ("", "invalido"), ("2026-09-02", "2026-09-01")):
                with instancia.subTest(inicio=inicio, fim=fim), instancia.assertRaises(ErroServico):
                    listar_vendas(data_inicial=inicio, data_final=fim)
            consulta.assert_not_called()
