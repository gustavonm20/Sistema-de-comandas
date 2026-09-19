import unittest
from unittest.mock import patch

import mysql.connector

from aplicacao import aplicacao


class TestesAplicacao(unittest.TestCase):
    def teste_falha_banco_exibe_mensagem_sem_detalhes(instancia):
        with patch("aplicacao.obter_painel", side_effect=mysql.connector.Error("detalhe-interno-restrito")):
            resposta = aplicacao.test_client().get("/")
        instancia.assertEqual(resposta.status_code, 503)
        instancia.assertIn("Não foi possível conectar ao MySQL", resposta.get_data(as_text=True))
        instancia.assertNotIn("detalhe-interno-restrito", resposta.get_data(as_text=True))

    def teste_arquivos_estaticos_acessiveis(instancia):
        for caminho in ("css/estilo.css", "js/principal.js", "imagens/fluxopag-logotipo.png"):
            with instancia.subTest(caminho=caminho):
                resposta = aplicacao.test_client().get(f"/estaticos/{caminho}")
                instancia.assertEqual(resposta.status_code, 200)
                resposta.close()

    def teste_todos_modelos_compilam(instancia):
        for nome in aplicacao.jinja_env.list_templates():
            with instancia.subTest(template=nome):
                aplicacao.jinja_env.get_template(nome)
