import unittest
from datetime import date, datetime
from decimal import Decimal

from utilitarios import formatar_data_hora, formatar_valor, obter_intervalo_periodo, normalizar_nome, converter_valor


class TestesValores(unittest.TestCase):
    def teste_conversao_moeda_brasileira(instancia):
        instancia.assertEqual(converter_valor("R$ 1.234,50"), Decimal("1234.50"))

    def teste_conversao_moeda_simples(instancia):
        instancia.assertEqual(converter_valor("12,90"), Decimal("12.90"))

    def teste_rejeita_valor_invalido(instancia):
        instancia.assertIsNone(converter_valor("abc"))

    def teste_rejeita_valor_nao_finito_e_fora_limite(instancia):
        for valor in ("NaN", "sNaN", "Infinity", "-Infinity", "1e1000000", "100000000"):
            with instancia.subTest(valor=valor):
                instancia.assertIsNone(converter_valor(valor))

    def teste_formatacao_moeda_brasileira(instancia):
        instancia.assertEqual(formatar_valor(1234.5), "R$ 1.234,50")


class TestesDatas(unittest.TestCase):
    def teste_formatacao_data_hora(instancia):
        valor = datetime(2026, 9, 9, 14, 5)
        instancia.assertEqual(formatar_data_hora(valor), "14:05  09/09/2026")

    def teste_periodo_diario(instancia):
        resultado = obter_intervalo_periodo("diario", date(2026, 9, 9))
        instancia.assertEqual(resultado["inicio"], datetime(2026, 9, 9, 0, 0))
        instancia.assertEqual(resultado["fim"], datetime(2026, 9, 10, 0, 0))
        instancia.assertEqual(resultado["inicio_anterior"], datetime(2026, 9, 8, 0, 0))

    def teste_periodo_semanal_comeca_segunda(instancia):
        resultado = obter_intervalo_periodo("semanal", date(2026, 9, 9))
        instancia.assertEqual(resultado["inicio"], datetime(2026, 9, 7, 0, 0))
        instancia.assertEqual(resultado["fim"], datetime(2026, 9, 14, 0, 0))

    def teste_periodo_mensal_atravessa_ano(instancia):
        resultado = obter_intervalo_periodo("mensal", date(2026, 12, 20))
        instancia.assertEqual(resultado["inicio"], datetime(2026, 12, 1, 0, 0))
        instancia.assertEqual(resultado["fim"], datetime(2027, 1, 1, 0, 0))

    def teste_mes_anterior_respeita_calendario(instancia):
        for atual, esperado in ((date(2026, 3, 15), datetime(2026, 2, 1)),
                                  (date(2024, 3, 1), datetime(2024, 2, 1)),
                                  (date(2026, 1, 2), datetime(2025, 12, 1))):
            with instancia.subTest(atual=atual):
                instancia.assertEqual(obter_intervalo_periodo("mensal", atual)["inicio_anterior"], esperado)


class TestesTextos(unittest.TestCase):
    def teste_normalizacao_nome(instancia):
        instancia.assertEqual(normalizar_nome("  Café   Duplo  "), "café duplo")


if __name__ == "__main__":
    unittest.main()
