import os
import secrets
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from banco import fechar_banco
from servicos import (
    ErroServico,
    adicionar_item_pedido,
    fechar_operacao,
    fechar_pedido,
    criar_cartao_comanda,
    criar_pedido,
    criar_produto,
    obter_painel,
    obter_estabelecimento,
    obter_operacao_aberta,
    obter_pedido,
    obter_produto,
    obter_resumo,
    obter_venda,
    listar_categorias,
    listar_cartoes_comanda,
    listar_pedidos_abertos,
    listar_produtos,
    listar_vendas,
    abrir_operacao,
    remover_item_pedido,
    alterar_situacao_cartao,
    alterar_situacao_produto,
    atualizar_estabelecimento,
    atualizar_item_pedido,
    atualizar_produto,
)
from utilitarios import formatar_data_hora, formatar_valor


load_dotenv(Path(__file__).with_name(".env"))
aplicacao = Flask(__name__, template_folder="modelos", static_folder="estaticos", static_url_path="/estaticos")
aplicacao.config.update(
    SECRET_KEY=os.getenv("FLASK_CHAVE_SECRETA") or secrets.token_hex(32),
    MYSQL_SERVIDOR=os.getenv("MYSQL_SERVIDOR", "127.0.0.1"),
    MYSQL_PORTA=int(os.getenv("MYSQL_PORTA", "3306")),
    MYSQL_USUARIO=os.getenv("MYSQL_USUARIO", "root"),
    MYSQL_SENHA=os.getenv("MYSQL_SENHA", ""),
    MYSQL_BANCO=os.getenv("MYSQL_BANCO", "comandas"),
)
aplicacao.teardown_appcontext(fechar_banco)


NOMES_PAGAMENTO = {
    "dinheiro": "Dinheiro",
    "pix": "Pix",
    "debito": "Débito",
    "credito": "Crédito",
}


@aplicacao.context_processor
def incluir_utilitarios_modelos():
    return {
        "formatar_valor": formatar_valor,
        "formatar_data_hora": formatar_data_hora,
        "nome_pagamento": lambda valor: NOMES_PAGAMENTO.get(valor, valor),
    }


def renderizar_pagina(nome_modelo, **contexto):
    contexto.setdefault("estabelecimento", obter_estabelecimento())
    contexto.setdefault("operacao", obter_operacao_aberta())
    return render_template(nome_modelo, **contexto)


@aplicacao.errorhandler(mysql.connector.Error)
def tratar_erro_banco(erro):
    aplicacao.logger.error("Erro no banco: %s", erro)
    return render_template("erro_banco.html"), 503


@aplicacao.errorhandler(ErroServico)
def tratar_erro_servico(erro):
    return render_template("erro.html", mensagem=str(erro)), 400


@aplicacao.route("/")
def painel():
    return renderizar_pagina("painel.html", pagina_ativa="painel", painel=obter_painel())


@aplicacao.route("/produtos")
def produtos():
    busca = request.args.get("busca", "").strip()
    id_categoria = request.args.get("id_categoria", type=int)
    situacao = request.args.get("situacao", "todos")
    return renderizar_pagina(
        "produtos.html",
        pagina_ativa="produtos",
        produtos=listar_produtos(busca, id_categoria, situacao),
        categorias=listar_categorias(),
        busca=busca,
        categoria_selecionada=id_categoria,
        situacao_selecionada=situacao,
    )


@aplicacao.route("/produtos/novo", methods=["GET", "POST"])
def criar_produto_rota():
    if request.method == "POST":
        try:
            criar_produto(request.form.get("nome"), request.form.get("preco"), request.form.get("id_categoria"))
            flash("Produto cadastrado com sucesso.", "sucesso")
            return redirect(url_for("produtos"))
        except ErroServico as erro:
            flash(str(erro), "erro")

    return renderizar_pagina(
        "formulario_produto.html",
        pagina_ativa="produtos",
        categorias=listar_categorias(),
        produto=None,
        titulo_pagina="Novo produto",
    )


@aplicacao.route("/produtos/<int:id_produto>/editar", methods=["GET", "POST"])
def editar_produto_rota(id_produto):
    produto = obter_produto(id_produto)
    if request.method == "POST":
        try:
            atualizar_produto(
                id_produto,
                request.form.get("nome"),
                request.form.get("preco"),
                request.form.get("id_categoria"),
            )
            flash("Produto atualizado com sucesso.", "sucesso")
            return redirect(url_for("produtos"))
        except ErroServico as erro:
            flash(str(erro), "erro")

    return renderizar_pagina(
        "formulario_produto.html",
        pagina_ativa="produtos",
        categorias=listar_categorias(),
        produto=produto,
        titulo_pagina="Editar produto",
    )


@aplicacao.post("/produtos/<int:id_produto>/situacao")
def situacao_produto(id_produto):
    try:
        ativo = request.form.get("ativo") == "true"
        alterar_situacao_produto(id_produto, ativo)
        flash("Situação do produto atualizada.", "sucesso")
    except ErroServico as erro:
        flash(str(erro), "erro")
    return redirect(url_for("produtos"))


@aplicacao.route("/cartoes", methods=["GET", "POST"])
def cartoes():
    if request.method == "POST":
        try:
            criar_cartao_comanda(request.form.get("numero_cartao"))
            flash("Cartão de comanda criado.", "sucesso")
            return redirect(url_for("cartoes"))
        except ErroServico as erro:
            flash(str(erro), "erro")

    situacao = request.args.get("situacao", "todos")
    return renderizar_pagina(
        "cartoes.html",
        pagina_ativa="pedidos",
        cartoes=listar_cartoes_comanda(situacao),
        situacao_selecionada=situacao,
    )


@aplicacao.post("/cartoes/<int:id_cartao>/situacao")
def situacao_cartao(id_cartao):
    try:
        ativo = request.form.get("ativo") == "true"
        alterar_situacao_cartao(id_cartao, ativo)
        flash("Situação da comanda atualizada.", "sucesso")
    except ErroServico as erro:
        flash(str(erro), "erro")
    return redirect(url_for("cartoes"))


@aplicacao.route("/pedidos")
def pedidos():
    tipo_atendimento = request.args.get("tipo_atendimento", "todos")
    return renderizar_pagina(
        "pedidos.html",
        pagina_ativa="pedidos",
        pedidos=listar_pedidos_abertos(tipo_atendimento),
        atendimento_selecionado=tipo_atendimento,
    )


@aplicacao.route("/pedidos/novo", methods=["GET", "POST"])
def criar_pedido_rota():
    if request.method == "POST":
        try:
            id_pedido = criar_pedido(
                request.form.get("id_cartao"),
                request.form.get("tipo_atendimento"),
                request.form.get("identificacao_atendimento"),
                request.form.get("observacao"),
            )
            flash("Comanda aberta com sucesso.", "sucesso")
            return redirect(url_for("detalhes_pedido", id_pedido=id_pedido))
        except ErroServico as erro:
            flash(str(erro), "erro")

    return renderizar_pagina(
        "novo_pedido.html",
        pagina_ativa="pedidos",
        cartoes=listar_cartoes_comanda("disponivel"),
    )


@aplicacao.route("/pedidos/<int:id_pedido>")
def detalhes_pedido(id_pedido):
    busca_produto = request.args.get("busca_produto", "").strip()
    return renderizar_pagina(
        "detalhes_pedido.html",
        pagina_ativa="pedidos",
        pedido=obter_pedido(id_pedido),
        produtos=listar_produtos(busca_produto, situacao="ativo"),
        busca_produto=busca_produto,
    )


@aplicacao.post("/pedidos/<int:id_pedido>/itens")
def adicionar_item_rota(id_pedido):
    try:
        adicionar_item_pedido(id_pedido, request.form.get("id_produto"), request.form.get("quantidade", 1))
        flash("Produto adicionado à comanda.", "sucesso")
    except ErroServico as erro:
        flash(str(erro), "erro")
    return redirect(url_for("detalhes_pedido", id_pedido=id_pedido))


@aplicacao.post("/pedidos/<int:id_pedido>/itens/<int:id_item>/quantidade")
def atualizar_item_rota(id_pedido, id_item):
    try:
        atualizar_item_pedido(id_pedido, id_item, request.form.get("quantidade"))
    except ErroServico as erro:
        flash(str(erro), "erro")
    return redirect(url_for("detalhes_pedido", id_pedido=id_pedido))


@aplicacao.post("/pedidos/<int:id_pedido>/itens/<int:id_item>/remover")
def remover_item_rota(id_pedido, id_item):
    try:
        remover_item_pedido(id_pedido, id_item)
        flash("Produto removido da comanda.", "sucesso")
    except ErroServico as erro:
        flash(str(erro), "erro")
    return redirect(url_for("detalhes_pedido", id_pedido=id_pedido))


@aplicacao.route("/pedidos/<int:id_pedido>/pagamento", methods=["GET", "POST"])
def pagamento(id_pedido):
    pedido = obter_pedido(id_pedido)
    if request.method == "POST":
        try:
            id_venda = fechar_pedido(
                id_pedido,
                request.form.get("forma_pagamento"),
                request.form.get("valor_recebido"),
            )
            flash("Pagamento registrado e comanda liberada.", "sucesso")
            return redirect(url_for("detalhes_venda", id_venda=id_venda))
        except ErroServico as erro:
            flash(str(erro), "erro")

    return renderizar_pagina("pagamento.html", pagina_ativa="pedidos", pedido=pedido)


@aplicacao.route("/historico")
def historico():
    filtros = {
        "busca": request.args.get("busca", "").strip(),
        "forma_pagamento": request.args.get("forma_pagamento", "todos"),
        "data_inicial": request.args.get("data_inicial", ""),
        "data_final": request.args.get("data_final", ""),
    }
    return renderizar_pagina(
        "historico.html",
        pagina_ativa="historico",
        vendas=listar_vendas(**filtros),
        filtros=filtros,
    )


@aplicacao.route("/vendas/<int:id_venda>")
def detalhes_venda(id_venda):
    return renderizar_pagina(
        "detalhes_venda.html",
        pagina_ativa="historico",
        venda=obter_venda(id_venda),
    )


@aplicacao.route("/resumos")
def resumos():
    periodo = request.args.get("periodo", "diario")
    if periodo not in {"diario", "semanal", "mensal"}:
        periodo = "diario"
    return renderizar_pagina(
        "resumos.html",
        pagina_ativa="painel",
        resumo=obter_resumo(periodo),
    )


@aplicacao.route("/conta", methods=["GET", "POST"])
def conta():
    if request.method == "POST":
        try:
            atualizar_estabelecimento(
                request.form.get("nome"),
                request.form.get("correio"),
                request.form.get("tipo_estabelecimento"),
            )
            flash("Dados do estabelecimento atualizados.", "sucesso")
            return redirect(url_for("conta"))
        except ErroServico as erro:
            flash(str(erro), "erro")

    return renderizar_pagina("conta.html", pagina_ativa="conta")


@aplicacao.post("/operacao/abrir")
def abrir_operacao_rota():
    try:
        abrir_operacao(request.form.get("caixa_inicial"))
        flash("Dia iniciado e caixa aberto.", "sucesso")
    except ErroServico as erro:
        flash(str(erro), "erro")
    return redirect(url_for("conta"))


@aplicacao.post("/operacao/fechar")
def fechar_operacao_rota():
    try:
        fechar_operacao(request.form.get("caixa_contado"), request.form.get("justificativa_diferenca"))
        flash("Caixa conferido e dia finalizado.", "sucesso")
    except ErroServico as erro:
        flash(str(erro), "erro")
    return redirect(url_for("conta"))


if __name__ == "__main__":
    aplicacao.run(host="127.0.0.1", debug=False)
