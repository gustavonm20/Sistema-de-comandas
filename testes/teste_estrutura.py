import ast
import struct
import unittest
from pathlib import Path


RAIZ_PROJETO = Path(__file__).resolve().parents[1]


class TestesEstrutura(unittest.TestCase):
    def teste_arquivos_necessarios_existem(instancia):
        arquivos_necessarios = [
            "aplicacao.py",
            "banco.py",
            "servicos.py",
            "utilitarios.py",
            "banco_dados/estrutura.sql",
            "estaticos/css/estilo.css",
            "estaticos/js/principal.js",
            "modelos/base.html",
            "modelos/painel.html",
            "modelos/produtos.html",
            "modelos/pedidos.html",
            "modelos/detalhes_pedido.html",
            "modelos/pagamento.html",
            "modelos/historico.html",
            "modelos/resumos.html",
            "modelos/conta.html",
        ]
        for caminho_relativo in arquivos_necessarios:
            with instancia.subTest(caminho=caminho_relativo):
                instancia.assertTrue((RAIZ_PROJETO / caminho_relativo).is_file())

    def teste_arquivos_python_com_sintaxe_valida(instancia):
        for caminho in RAIZ_PROJETO.glob("*.py"):
            with instancia.subTest(caminho=caminho.name):
                ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))

    def teste_arquivos_interface_proibidos_ausentes(instancia):
        extensoes_proibidas = {".jsx", ".tsx", ".ts", ".vue", ".svelte"}
        nomes_proibidos = {"package.json", "package-lock.json", "vite.config.js"}
        encontrados = []
        for caminho in RAIZ_PROJETO.rglob("*"):
            if any(parte in {".git", ".venv", "venv", "__pycache__"} for parte in caminho.parts):
                continue
            if caminho.is_file() and (caminho.suffix in extensoes_proibidas or caminho.name in nomes_proibidos):
                encontrados.append(str(caminho.relative_to(RAIZ_PROJETO)))
        instancia.assertEqual(encontrados, [])

    def teste_dependencias_apenas_python(instancia):
        linhas = [
            linha.strip().lower()
            for linha in (RAIZ_PROJETO / "dependencias.txt").read_text(encoding="utf-8").splitlines()
            if linha.strip() and not linha.startswith("#")
        ]
        instancia.assertEqual(len(linhas), 3)
        instancia.assertTrue(linhas[0].startswith("flask"))
        instancia.assertTrue(linhas[1].startswith("mysql-connector-python"))
        instancia.assertTrue(linhas[2].startswith("python-dotenv"))

    def teste_estrutura_contem_tabelas_e_regras(instancia):
        sql = (RAIZ_PROJETO / "banco_dados/estrutura.sql").read_text(encoding="utf-8").lower()
        tabelas_esperadas = {
            "estabelecimentos",
            "categorias",
            "produtos",
            "cartoes_comanda",
            "operacoes_diarias",
            "pedidos",
            "itens_pedido",
            "vendas",
            "registros_auditoria",
        }
        for tabela in tabelas_esperadas:
            with instancia.subTest(tabela=tabela):
                instancia.assertIn(f"create table if not exists {tabela}", sql)
        instancia.assertIn("check (numero_cartao regexp '^[0-9]{4}$')", sql)
        instancia.assertIn("unique (id_cartao_aberto)", sql)
        instancia.assertIn("unique (id_pedido)", sql)

    def teste_tema_salvo_e_paleta_escura(instancia):
        javascript = (RAIZ_PROJETO / "estaticos/js/principal.js").read_text(encoding="utf-8")
        folha_estilos = (RAIZ_PROJETO / "estaticos/css/estilo.css").read_text(encoding="utf-8")
        instancia.assertIn('localStorage.setItem("fluxopag-tema"', javascript)
        instancia.assertIn('html[data-tema="escuro"]', folha_estilos)

    def teste_dimensoes_imagens_fornecidas(instancia):
        imagens_esperadas = {
            "estaticos/imagens/fluxopag-marca-original.png": (397, 180),
            "estaticos/imagens/fluxopag-logotipo.png": (42, 44),
            "estaticos/imagens/icones-menu/painel-ativo.png": (16, 16),
            "estaticos/imagens/icones-menu/produtos-ativo.png": (18, 18),
            "estaticos/imagens/icones-menu/pedidos-ativo.png": (18, 18),
            "estaticos/imagens/icones-menu/historico-ativo.png": (18, 18),
        }
        for caminho_relativo, tamanho_esperado in imagens_esperadas.items():
            with instancia.subTest(caminho=caminho_relativo):
                caminho = RAIZ_PROJETO / caminho_relativo
                with caminho.open("rb") as arquivo_imagem:
                    cabecalho = arquivo_imagem.read(24)
                instancia.assertEqual(cabecalho[:8], b"\x89PNG\r\n\x1a\n")
                instancia.assertEqual(struct.unpack(">II", cabecalho[16:24]), tamanho_esperado)


if __name__ == "__main__":
    unittest.main()
