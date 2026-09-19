from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

from modelos import SessaoCaixa, Pedido, ItemPedido, Produto, Venda, agora_iso
from armazenamento import ArmazenamentoJson


class ErroNegocio(Exception):
    pass


class ServicoComandas:
    MAXIMO_COMANDAS = 20
    FORMAS_PAGAMENTO = {"1": "Dinheiro", "2": "Pix", "3": "Crédito", "4": "Débito"}

    def __init__(instancia, arquivo_dados: Path) -> None:
        instancia.armazenamento = ArmazenamentoJson(arquivo_dados)
        instancia.produtos: list[Produto] = []
        instancia.pedidos: list[Pedido] = []
        instancia.vendas: list[Venda] = []
        instancia.sessoes_caixa: list[SessaoCaixa] = []
        instancia.recarregar()

    def recarregar(instancia) -> None:
        dados = instancia.armazenamento.carregar()
        instancia.produtos = [Produto.de_dicionario(item) for item in dados["produtos"]]
        instancia.pedidos = [Pedido.de_dicionario(item) for item in dados["pedidos_abertos"]]
        instancia.vendas = [Venda.de_dicionario(item) for item in dados["vendas"]]
        instancia.sessoes_caixa = [SessaoCaixa.de_dicionario(item) for item in dados["sessoes_caixa"]]

    def salvar(instancia) -> None:
        instancia.armazenamento.salvar({
            "produtos": [item.para_dicionario() for item in instancia.produtos],
            "pedidos_abertos": [item.para_dicionario() for item in instancia.pedidos],
            "vendas": [item.para_dicionario() for item in instancia.vendas],
            "sessoes_caixa": [item.para_dicionario() for item in instancia.sessoes_caixa],
        })

    @property
    def sessao_caixa_atual(instancia) -> SessaoCaixa | None:
        return next((sessao for sessao in reversed(instancia.sessoes_caixa) if sessao.esta_aberto), None)

    def adicionar_produto(instancia, nome: str, preco_centavos: int, categoria: str) -> Produto:
        if not nome.strip() or not categoria.strip():
            raise ErroNegocio("Nome e categoria são obrigatórios.")
        if preco_centavos <= 0:
            raise ErroNegocio("O preço deve ser maior que zero.")
        produto = Produto(instancia._proximo_id(instancia.produtos, "id_produto"), nome.strip(), preco_centavos, categoria.strip())
        instancia.produtos.append(produto)
        instancia.salvar()
        return produto

    def encontrar_produto(instancia, id_produto: int, exigir_ativo: bool = False) -> Produto:
        produto = next((item for item in instancia.produtos if item.id_produto == id_produto), None)
        if produto is None:
            raise ErroNegocio("Produto não encontrado.")
        if exigir_ativo and not produto.ativo:
            raise ErroNegocio("Este produto está desativado.")
        return produto

    def pesquisar_produtos(instancia, termo: str) -> list[Produto]:
        normalizado = termo.strip().casefold()
        return [item for item in instancia.produtos if normalizado in item.nome.casefold() or normalizado in item.categoria.casefold()]

    def editar_produto(instancia, id_produto: int, nome: str, preco_centavos: int, categoria: str) -> Produto:
        produto = instancia.encontrar_produto(id_produto)
        if not nome.strip() or not categoria.strip() or preco_centavos <= 0:
            raise ErroNegocio("Informe nome, preço e categoria válidos.")
        produto.nome = nome.strip()
        produto.preco_centavos = preco_centavos
        produto.categoria = categoria.strip()
        instancia.salvar()
        return produto

    def desativar_produto(instancia, id_produto: int) -> None:
        produto = instancia.encontrar_produto(id_produto)
        if not produto.ativo:
            raise ErroNegocio("O produto já está desativado.")
        produto.ativo = False
        instancia.salvar()

    def abrir_caixa(instancia, saldo_inicial_centavos: int) -> SessaoCaixa:
        if instancia.sessao_caixa_atual:
            raise ErroNegocio("O dia já foi iniciado.")
        if saldo_inicial_centavos < 0:
            raise ErroNegocio("O saldo inicial não pode ser negativo.")
        sessao = SessaoCaixa(instancia._proximo_id(instancia.sessoes_caixa, "id_sessao"), agora_iso(), saldo_inicial_centavos)
        instancia.sessoes_caixa.append(sessao)
        instancia.salvar()
        return sessao

    def fechar_caixa(instancia, caixa_contado_centavos: int) -> SessaoCaixa:
        sessao = instancia.sessao_caixa_atual
        if sessao is None:
            raise ErroNegocio("Não existe um dia aberto.")
        if instancia.pedidos:
            numeros = ", ".join(str(pedido.numero_comanda) for pedido in instancia.pedidos)
            raise ErroNegocio(f"Fechamento bloqueado. Comandas abertas: {numeros}.")
        if caixa_contado_centavos < 0:
            raise ErroNegocio("O valor contado não pode ser negativo.")
        vendas_dinheiro = sum(
            venda.total_centavos for venda in instancia.vendas
            if venda.id_sessao_caixa == sessao.id_sessao and venda.forma_pagamento == "Dinheiro"
        )
        esperado = sessao.saldo_inicial_centavos + vendas_dinheiro
        sessao.fechado_em = agora_iso()
        sessao.caixa_esperado_centavos = esperado
        sessao.caixa_contado_centavos = caixa_contado_centavos
        sessao.diferenca_centavos = caixa_contado_centavos - esperado
        instancia.salvar()
        return sessao

    def abrir_pedido(instancia, numero_comanda: int) -> Pedido:
        if instancia.sessao_caixa_atual is None:
            raise ErroNegocio("Inicie o dia antes de abrir comandas.")
        instancia._validar_numero_comanda(numero_comanda)
        if any(item.numero_comanda == numero_comanda for item in instancia.pedidos):
            raise ErroNegocio("Esta comanda já está aberta.")
        pedido = Pedido(numero_comanda, agora_iso())
        instancia.pedidos.append(pedido)
        instancia.salvar()
        return pedido

    def encontrar_pedido(instancia, numero_comanda: int) -> Pedido:
        pedido = next((item for item in instancia.pedidos if item.numero_comanda == numero_comanda), None)
        if pedido is None:
            raise ErroNegocio("Comanda não está aberta.")
        return pedido

    def adicionar_item(instancia, numero_comanda: int, id_produto: int, quantidade: int) -> None:
        if quantidade <= 0:
            raise ErroNegocio("A quantidade deve ser maior que zero.")
        pedido = instancia.encontrar_pedido(numero_comanda)
        produto = instancia.encontrar_produto(id_produto, exigir_ativo=True)
        existente = next((item for item in pedido.itens if item.id_produto == id_produto), None)
        if existente:
            existente.quantidade += quantidade
        else:
            pedido.itens.append(ItemPedido(produto.id_produto, produto.nome, produto.preco_centavos, quantidade))
        instancia.salvar()

    def remover_item(instancia, numero_comanda: int, id_produto: int, quantidade: int) -> None:
        if quantidade <= 0:
            raise ErroNegocio("A quantidade deve ser maior que zero.")
        pedido = instancia.encontrar_pedido(numero_comanda)
        item = next((item for item in pedido.itens if item.id_produto == id_produto), None)
        if item is None:
            raise ErroNegocio("Produto não está nesta comanda.")
        if quantidade > item.quantidade:
            raise ErroNegocio("A quantidade informada é maior que a registrada.")
        item.quantidade -= quantidade
        if item.quantidade == 0:
            pedido.itens.remove(item)
        instancia.salvar()

    def fechar_pedido(instancia, numero_comanda: int, opcao_pagamento: str) -> Venda:
        sessao = instancia.sessao_caixa_atual
        if sessao is None:
            raise ErroNegocio("Não existe um dia aberto.")
        pedido = instancia.encontrar_pedido(numero_comanda)
        if not pedido.itens:
            raise ErroNegocio("Não é possível fechar uma comanda vazia.")
        forma_pagamento = instancia.FORMAS_PAGAMENTO.get(opcao_pagamento)
        if forma_pagamento is None:
            raise ErroNegocio("Forma de pagamento inválida.")
        venda = Venda(
            id_venda=instancia._proximo_id(instancia.vendas, "id_venda"),
            numero_comanda=pedido.numero_comanda,
            itens=pedido.itens.copy(),
            total_centavos=pedido.total_centavos,
            forma_pagamento=forma_pagamento,
            fechado_em=agora_iso(),
            id_sessao_caixa=sessao.id_sessao,
        )
        instancia.vendas.append(venda)
        instancia.pedidos.remove(pedido)
        instancia.salvar()
        return venda

    def resumo_periodo(instancia, periodo: str, referencia: date | None = None) -> dict[str, object]:
        referencia = referencia or date.today()
        inicio, fim, inicio_anterior, fim_anterior = instancia._limites_periodo(periodo, referencia)
        vendas_atuais = instancia._vendas_entre(inicio, fim)
        vendas_anteriores = instancia._vendas_entre(inicio_anterior, fim_anterior)
        total = sum(item.total_centavos for item in vendas_atuais)
        total_anterior = sum(item.total_centavos for item in vendas_anteriores)
        variacao = None if total_anterior == 0 else ((total - total_anterior) / total_anterior) * 100
        pagamentos: dict[str, int] = {}
        produtos: dict[str, int] = {}
        for venda in vendas_atuais:
            pagamentos[venda.forma_pagamento] = pagamentos.get(venda.forma_pagamento, 0) + venda.total_centavos
            for item in venda.itens:
                produtos[item.nome_produto] = produtos.get(item.nome_produto, 0) + item.quantidade
        produtos_mais_vendidos = sorted(produtos.items(), key=lambda item: (-item[1], item[0]))[:5]
        return {
            "inicio": inicio,
            "fim": fim,
            "quantidade_vendas": len(vendas_atuais),
            "total_centavos": total,
            "media_centavos": total // len(vendas_atuais) if vendas_atuais else 0,
            "pagamentos": pagamentos,
            "produtos_mais_vendidos": produtos_mais_vendidos,
            "total_anterior_centavos": total_anterior,
            "variacao_percentual": variacao,
        }

    def _vendas_entre(instancia, inicio: date, fim: date) -> list[Venda]:
        return [venda for venda in instancia.vendas if inicio <= datetime.fromisoformat(venda.fechado_em).date() <= fim]

    @staticmethod
    def _limites_periodo(periodo: str, referencia: date) -> tuple[date, date, date, date]:
        if periodo == "dia":
            return referencia, referencia, referencia - timedelta(days=1), referencia - timedelta(days=1)
        if periodo == "semana":
            inicio = referencia - timedelta(days=referencia.weekday())
            fim = inicio + timedelta(days=6)
            return inicio, fim, inicio - timedelta(days=7), fim - timedelta(days=7)
        if periodo == "mes":
            inicio = referencia.replace(day=1)
            proximo_mes = (inicio.replace(day=28) + timedelta(days=4)).replace(day=1)
            fim = proximo_mes - timedelta(days=1)
            fim_anterior = inicio - timedelta(days=1)
            inicio_anterior = fim_anterior.replace(day=1)
            return inicio, fim, inicio_anterior, fim_anterior
        raise ErroNegocio("Período inválido.")

    @staticmethod
    def _proximo_id(itens: list[object], atributo: str) -> int:
        return max((getattr(item, atributo) for item in itens), default=0) + 1

    def _validar_numero_comanda(instancia, numero_comanda: int) -> None:
        if not 1 <= numero_comanda <= instancia.MAXIMO_COMANDAS:
            raise ErroNegocio(f"A comanda deve estar entre 1 e {instancia.MAXIMO_COMANDAS}.")
