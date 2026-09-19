from datetime import datetime
from decimal import Decimal

import mysql.connector

from banco import buscar_todos, buscar_um, obter_banco
from utilitarios import obter_intervalo_periodo, normalizar_nome, converter_valor


class ErroServico(Exception):
    pass


def registrar_auditoria(cursor, acao, tipo_entidade, id_entidade=None, detalhe=None):
    cursor.execute(
        """
        INSERT INTO registros_auditoria (responsavel, acao, tipo_entidade, id_entidade, detalhe)
        VALUES (%s, %s, %s, %s, %s)
        """,
        ("administrador-local", acao, tipo_entidade, id_entidade, detalhe),
    )


def executar_com_auditoria(consulta, parametros, acao, tipo_entidade, id_entidade=None, detalhe=None):
    banco = obter_banco()
    cursor = banco.cursor()
    try:
        banco.start_transaction()
        cursor.execute(consulta, parametros)
        id_criado = cursor.lastrowid
        linhas_afetadas = cursor.rowcount
        if id_criado or linhas_afetadas > 0:
            registrar_auditoria(cursor, acao, tipo_entidade, id_entidade or id_criado, detalhe)
        banco.commit()
        return id_criado, linhas_afetadas
    except Exception:
        banco.rollback()
        raise
    finally:
        cursor.close()


def obter_painel():
    indicadores = buscar_um(
        """
        SELECT
            (SELECT COUNT(*) FROM pedidos WHERE situacao = 'aberto') AS pedidos_abertos,
            COUNT(id_venda) AS vendas_concluidas,
            COALESCE(SUM(valor_total), 0) AS faturamento,
            COALESCE(AVG(valor_total), 0) AS valor_medio_venda
        FROM vendas
        WHERE DATE(vendido_em) = CURDATE()
        """
    )
    ultimos_pedidos = buscar_todos(
        """
        SELECT o.id_pedido, c.numero_cartao, o.identificacao_atendimento, o.aberto_em,
               COALESCE(SUM(i.quantidade * i.preco_unitario), 0) AS total
        FROM pedidos o
        JOIN cartoes_comanda c ON c.id_cartao = o.id_cartao
        LEFT JOIN itens_pedido i ON i.id_pedido = o.id_pedido
        WHERE o.situacao = 'aberto'
        GROUP BY o.id_pedido, c.numero_cartao, o.identificacao_atendimento, o.aberto_em
        ORDER BY o.aberto_em DESC
        LIMIT 5
        """
    )
    registros_por_hora = buscar_todos(
        """
        SELECT HOUR(vendido_em) AS hora_venda, SUM(valor_total) AS faturamento
        FROM vendas
        WHERE DATE(vendido_em) = CURDATE()
        GROUP BY HOUR(vendido_em)
        ORDER BY hora_venda
        """
    )
    valores_por_hora = {int(registro["hora_venda"]): registro["faturamento"] for registro in registros_por_hora}
    maximo = max((Decimal(str(valor)) for valor in valores_por_hora.values()), default=Decimal("0"))
    evolucao = []
    for hora in range(8, 21):
        valor = Decimal(str(valores_por_hora.get(hora, 0)))
        altura = int((valor / maximo) * 100) if maximo > 0 else 0
        evolucao.append({"rotulo": f"{hora:02d}h", "valor": valor, "altura": max(altura, 4) if valor else 2})

    return {
        "indicadores": indicadores,
        "ultimos_pedidos": ultimos_pedidos,
        "evolucao": evolucao,
    }


def listar_categorias():
    return buscar_todos("SELECT id_categoria, nome, ativo FROM categorias ORDER BY nome")


def listar_produtos(busca="", id_categoria=None, situacao="todos"):
    condicoes = ["1 = 1"]
    parametros = []

    if busca:
        condicoes.append("LOWER(p.nome) LIKE %s")
        parametros.append(f"%{normalizar_nome(busca)}%")
    if id_categoria:
        condicoes.append("p.id_categoria = %s")
        parametros.append(id_categoria)
    if situacao == "ativo":
        condicoes.append("p.ativo = TRUE")
    elif situacao == "inativo":
        condicoes.append("p.ativo = FALSE")

    return buscar_todos(
        f"""
        SELECT p.id_produto, p.nome, p.preco, p.ativo,
               p.id_categoria, c.nome AS nome_categoria
        FROM produtos p
        JOIN categorias c ON c.id_categoria = p.id_categoria
        WHERE {' AND '.join(condicoes)}
        ORDER BY p.ativo DESC, p.nome
        """,
        tuple(parametros),
    )


def obter_produto(id_produto):
    produto = buscar_um(
        """
        SELECT p.id_produto, p.nome, p.preco, p.ativo,
               p.id_categoria, c.nome AS nome_categoria
        FROM produtos p
        JOIN categorias c ON c.id_categoria = p.id_categoria
        WHERE p.id_produto = %s
        """,
        (id_produto,),
    )
    if not produto:
        raise ErroServico("Produto não encontrado.")
    return produto


def validar_produto(nome, texto_preco, id_categoria):
    nome_limpo = " ".join(str(nome or "").strip().split())
    preco = converter_valor(texto_preco)
    try:
        id_categoria = int(id_categoria)
    except (TypeError, ValueError):
        id_categoria = 0

    if not 2 <= len(nome_limpo) <= 100:
        raise ErroServico("O nome do produto deve ter entre 2 e 100 caracteres.")
    if preco is None or preco <= 0:
        raise ErroServico("O preço precisa ser maior que zero.")
    categoria = buscar_um(
        "SELECT id_categoria FROM categorias WHERE id_categoria = %s AND ativo = TRUE",
        (id_categoria,),
    )
    if not categoria:
        raise ErroServico("Selecione uma categoria ativa.")
    return nome_limpo, preco, id_categoria


def criar_produto(nome, texto_preco, id_categoria):
    nome_limpo, preco, id_categoria = validar_produto(nome, texto_preco, id_categoria)
    try:
        id_produto, _ = executar_com_auditoria(
            """
            INSERT INTO produtos (nome, nome_normalizado, preco, id_categoria, ativo)
            VALUES (%s, %s, %s, %s, TRUE)
            """,
            (nome_limpo, normalizar_nome(nome_limpo), preco, id_categoria),
            "produto.criado",
            "produto",
            detalhe=nome_limpo,
        )
        return id_produto
    except mysql.connector.IntegrityError as erro:
        raise ErroServico("Já existe um produto com esse nome.") from erro


def atualizar_produto(id_produto, nome, texto_preco, id_categoria):
    obter_produto(id_produto)
    nome_limpo, preco, id_categoria = validar_produto(nome, texto_preco, id_categoria)
    try:
        executar_com_auditoria(
            """
            UPDATE produtos
            SET nome = %s, nome_normalizado = %s, preco = %s, id_categoria = %s
            WHERE id_produto = %s
            """,
            (nome_limpo, normalizar_nome(nome_limpo), preco, id_categoria, id_produto),
            "produto.atualizado",
            "produto",
            id_produto,
            nome_limpo,
        )
    except mysql.connector.IntegrityError as erro:
        raise ErroServico("Já existe outro produto com esse nome.") from erro


def alterar_situacao_produto(id_produto, ativo):
    produto = obter_produto(id_produto)
    if bool(produto["ativo"]) == ativo:
        raise ErroServico("O produto já está com esse situacao.")
    executar_com_auditoria(
        "UPDATE produtos SET ativo = %s WHERE id_produto = %s",
        (ativo, id_produto),
        "produto.activated" if ativo else "produto.deactivated",
        "produto",
        id_produto,
        produto["nome"],
    )


def listar_cartoes_comanda(situacao="todos"):
    condicoes = ["1 = 1"]
    if situacao == "disponivel":
        condicoes.append("c.ativo = TRUE AND o.id_pedido IS NULL")
    elif situacao == "aberto":
        condicoes.append("o.id_pedido IS NOT NULL")
    elif situacao == "inativo":
        condicoes.append("c.ativo = FALSE")

    return buscar_todos(
        f"""
        SELECT c.id_cartao, c.numero_cartao, c.ativo, o.id_pedido,
               o.identificacao_atendimento, o.aberto_em,
               COALESCE(SUM(i.quantidade * i.preco_unitario), 0) AS total
        FROM cartoes_comanda c
        LEFT JOIN pedidos o ON o.id_cartao = c.id_cartao AND o.situacao = 'aberto'
        LEFT JOIN itens_pedido i ON i.id_pedido = o.id_pedido
        WHERE {' AND '.join(condicoes)}
        GROUP BY c.id_cartao, c.numero_cartao, c.ativo,
                 o.id_pedido, o.identificacao_atendimento, o.aberto_em
        ORDER BY c.numero_cartao
        """
    )


def criar_cartao_comanda(numero_cartao):
    numero_cartao = str(numero_cartao or "").strip()
    if len(numero_cartao) != 4 or not numero_cartao.isascii() or not numero_cartao.isdigit():
        raise ErroServico("O número da comanda deve possuir quatro dígitos.")
    try:
        executar_com_auditoria(
            "INSERT INTO cartoes_comanda (numero_cartao, ativo) VALUES (%s, TRUE)",
            (numero_cartao,),
            "cartao_comanda.criado",
            "cartao_comanda",
            detalhe=numero_cartao,
        )
    except mysql.connector.IntegrityError as erro:
        raise ErroServico("Já existe uma comanda com esse número.") from erro


def alterar_situacao_cartao(id_cartao, ativo):
    cartao = buscar_um(
        """
        SELECT c.numero_cartao,
               (SELECT id_pedido FROM pedidos WHERE id_cartao = c.id_cartao AND situacao = 'aberto' LIMIT 1) AS id_pedido_aberto
        FROM cartoes_comanda c
        WHERE c.id_cartao = %s
        """,
        (id_cartao,),
    )
    if not cartao:
        raise ErroServico("Cartão de comanda não encontrado.")
    if not ativo and cartao["id_pedido_aberto"]:
        raise ErroServico("Feche a comanda antes de desativar esse cartão.")
    executar_com_auditoria(
        "UPDATE cartoes_comanda SET ativo = %s WHERE id_cartao = %s",
        (ativo, id_cartao),
        "cartao_comanda.activated" if ativo else "cartao_comanda.deactivated",
        "cartao_comanda",
        id_cartao,
        cartao["numero_cartao"],
    )


def obter_operacao_aberta():
    operacao = buscar_um(
        """
        SELECT d.*,
               d.caixa_inicial + COALESCE((
                   SELECT SUM(s.valor_total)
                   FROM vendas s
                   JOIN pedidos o ON o.id_pedido = s.id_pedido
                   WHERE o.id_operacao = d.id_operacao
                     AND s.forma_pagamento = 'dinheiro'
               ), 0) AS caixa_esperado_atual
        FROM operacoes_diarias d
        WHERE d.situacao = 'aberto'
        ORDER BY d.id_operacao DESC
        LIMIT 1
        """
    )
    return operacao


def abrir_operacao(texto_caixa_inicial):
    caixa_inicial = converter_valor(texto_caixa_inicial)
    if caixa_inicial is None or caixa_inicial < 0:
        raise ErroServico("Informe um valor inicial válido.")
    try:
        executar_com_auditoria(
            "INSERT INTO operacoes_diarias (situacao, caixa_inicial) VALUES ('aberto', %s)",
            (caixa_inicial,),
            "operacao.aberto",
            "operacao_diaria",
            detalhe=str(caixa_inicial),
        )
    except mysql.connector.IntegrityError as erro:
        raise ErroServico("Já existe um dia em andamento.") from erro


def fechar_operacao(texto_caixa_contado, justificativa_diferenca):
    caixa_contado = converter_valor(texto_caixa_contado)
    observacao = " ".join(str(justificativa_diferenca or "").strip().split())
    if len(observacao) > 255:
        raise ErroServico("A observação deve ter no máximo 255 caracteres.")
    if caixa_contado is None or caixa_contado < 0:
        raise ErroServico("Informe o valor contado no caixa.")

    banco = obter_banco()
    cursor = banco.cursor(dictionary=True)
    try:
        banco.start_transaction()
        cursor.execute(
            "SELECT * FROM operacoes_diarias WHERE situacao = 'aberto' ORDER BY id_operacao DESC LIMIT 1 FOR UPDATE"
        )
        operacao = cursor.fetchone()
        if not operacao:
            raise ErroServico("Não existe um dia em andamento.")

        cursor.execute("SELECT COUNT(*) AS total FROM pedidos WHERE situacao = 'aberto'")
        if cursor.fetchone()["total"] > 0:
            raise ErroServico("Feche todas as comandas antes de finalizar o dia.")

        cursor.execute(
            """
            SELECT COALESCE(SUM(s.valor_total), 0) AS vendas_dinheiro
            FROM vendas s
            JOIN pedidos o ON o.id_pedido = s.id_pedido
            WHERE o.id_operacao = %s AND s.forma_pagamento = 'dinheiro'
            """,
            (operacao["id_operacao"],),
        )
        vendas_dinheiro = Decimal(str(cursor.fetchone()["vendas_dinheiro"]))
        caixa_esperado = Decimal(str(operacao["caixa_inicial"])) + vendas_dinheiro
        diferenca = caixa_contado - caixa_esperado
        if diferenca != 0 and len(observacao) < 5:
            raise ErroServico("Explique a diferença encontrada no caixa.")

        cursor.execute(
            """
            UPDATE operacoes_diarias
            SET situacao = 'fechado', caixa_esperado = %s, caixa_contado = %s,
                valor_diferenca = %s, justificativa_diferenca = %s, fechado_em = CURRENT_TIMESTAMP
            WHERE id_operacao = %s
            """,
            (caixa_esperado, caixa_contado, diferenca, observacao or None, operacao["id_operacao"]),
        )
        registrar_auditoria(cursor, "operacao.fechado", "operacao_diaria", operacao["id_operacao"], str(diferenca))
        banco.commit()
    except Exception:
        banco.rollback()
        raise
    finally:
        cursor.close()


def listar_pedidos_abertos(tipo_atendimento="todos"):
    condicao = ""
    parametros = ()
    if tipo_atendimento in {"mesa", "balcao", "retirada"}:
        condicao = "AND o.tipo_atendimento = %s"
        parametros = (tipo_atendimento,)
    return buscar_todos(
        f"""
        SELECT o.id_pedido, c.numero_cartao, o.tipo_atendimento, o.identificacao_atendimento,
               o.aberto_em, COALESCE(SUM(i.quantidade * i.preco_unitario), 0) AS total,
               COALESCE(SUM(i.quantidade), 0) AS quantidade_itens
        FROM pedidos o
        JOIN cartoes_comanda c ON c.id_cartao = o.id_cartao
        LEFT JOIN itens_pedido i ON i.id_pedido = o.id_pedido
        WHERE o.situacao = 'aberto' {condicao}
        GROUP BY o.id_pedido, c.numero_cartao, o.tipo_atendimento, o.identificacao_atendimento, o.aberto_em
        ORDER BY o.aberto_em
        """,
        parametros,
    )


def criar_pedido(id_cartao, tipo_atendimento, identificacao_atendimento="", observacao=""):
    try:
        id_cartao = int(id_cartao)
    except (TypeError, ValueError):
        raise ErroServico("Selecione uma comanda disponível.")
    if tipo_atendimento not in {"mesa", "balcao", "retirada"}:
        raise ErroServico("Selecione um tipo de atendimento.")

    identificacao_atendimento = " ".join(str(identificacao_atendimento or "").strip().split())
    observacao = " ".join(str(observacao or "").strip().split())
    if tipo_atendimento == "mesa" and not identificacao_atendimento:
        raise ErroServico("Informe o número ou a identificação da mesa.")
    if tipo_atendimento == "mesa":
        identificacao_atendimento = f"Mesa {identificacao_atendimento.removeprefix('Mesa ').removeprefix('mesa ')}"
    elif not identificacao_atendimento:
        identificacao_atendimento = "Balcão" if tipo_atendimento == "balcao" else "Retirada"
    if len(identificacao_atendimento) > 100 or len(observacao) > 255:
        raise ErroServico("Use até 100 caracteres na identificação e 255 na observação.")

    operacao = obter_operacao_aberta()
    if not operacao:
        raise ErroServico("Inicie o dia antes de abrir uma comanda.")
    cartao = buscar_um(
        "SELECT id_cartao FROM cartoes_comanda WHERE id_cartao = %s AND ativo = TRUE",
        (id_cartao,),
    )
    if not cartao:
        raise ErroServico("A comanda selecionada está indisponível.")

    try:
        id_pedido, _ = executar_com_auditoria(
            """
            INSERT INTO pedidos
                (id_cartao, id_operacao, tipo_atendimento, identificacao_atendimento, observacao, situacao)
            VALUES (%s, %s, %s, %s, %s, 'aberto')
            """,
            (id_cartao, operacao["id_operacao"], tipo_atendimento, identificacao_atendimento, observacao or None),
            "pedido.aberto",
            "pedido",
            detalhe=identificacao_atendimento,
        )
        return id_pedido
    except mysql.connector.IntegrityError as erro:
        raise ErroServico("Essa comanda já está aberta.") from erro


def obter_pedido(id_pedido):
    pedido = buscar_um(
        """
        SELECT o.*, c.numero_cartao,
               COALESCE((
                   SELECT SUM(i.quantidade * i.preco_unitario)
                   FROM itens_pedido i
                   WHERE i.id_pedido = o.id_pedido
               ), 0) AS total,
               COALESCE((
                   SELECT SUM(i.quantidade)
                   FROM itens_pedido i
                   WHERE i.id_pedido = o.id_pedido
               ), 0) AS quantidade_itens
        FROM pedidos o
        JOIN cartoes_comanda c ON c.id_cartao = o.id_cartao
        WHERE o.id_pedido = %s
        """,
        (id_pedido,),
    )
    if not pedido:
        raise ErroServico("Comanda não encontrada.")
    pedido["itens"] = buscar_todos(
        """
        SELECT id_item_pedido AS id_item, id_produto, nome_produto_historico, nome_categoria_historico,
               preco_unitario, quantidade, quantidade * preco_unitario AS total_item
        FROM itens_pedido
        WHERE id_pedido = %s
        ORDER BY id_item_pedido
        """,
        (id_pedido,),
    )
    return pedido


def adicionar_item_pedido(id_pedido, id_produto, quantidade):
    try:
        id_produto = int(id_produto)
        quantidade = int(quantidade)
    except (TypeError, ValueError):
        raise ErroServico("Selecione um produto e uma quantidade válida.")
    if quantidade < 1 or quantidade > 99:
        raise ErroServico("A quantidade deve ficar entre 1 e 99.")

    pedido = obter_pedido(id_pedido)
    if pedido["situacao"] != "aberto":
        raise ErroServico("Essa comanda já foi fechada.")
    quantidade_existente = sum(item["quantidade"] for item in pedido["itens"] if item["id_produto"] == id_produto)
    if quantidade_existente + quantidade > 99:
        raise ErroServico("A quantidade total do produto deve ficar entre 1 e 99.")
    produto = buscar_um(
        """
        SELECT p.id_produto, p.nome, p.preco, p.ativo, c.nome AS nome_categoria
        FROM produtos p
        JOIN categorias c ON c.id_categoria = p.id_categoria
        WHERE p.id_produto = %s
        """,
        (id_produto,),
    )
    if not produto or not produto["ativo"]:
        raise ErroServico("O produto selecionado está indisponível.")

    executar_com_auditoria(
        """
        INSERT INTO itens_pedido
            (id_pedido, id_produto, nome_produto_historico, nome_categoria_historico, preco_unitario, quantidade)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE quantidade = quantidade + VALUES(quantidade)
        """,
        (
            id_pedido,
            id_produto,
            produto["nome"],
            produto["nome_categoria"],
            produto["preco"],
            quantidade,
        ),
        "pedido.item_adicionado",
        "pedido",
        id_pedido,
        produto["nome"],
    )


def atualizar_item_pedido(id_pedido, id_item, quantidade):
    try:
        quantidade = int(quantidade)
    except (TypeError, ValueError):
        raise ErroServico("Informe uma quantidade válida.")
    if quantidade < 1 or quantidade > 99:
        raise ErroServico("A quantidade deve ficar entre 1 e 99.")
    pedido = obter_pedido(id_pedido)
    if pedido["situacao"] != "aberto":
        raise ErroServico("Essa comanda já foi fechada.")
    item = next((item for item in pedido["itens"] if item["id_item"] == id_item), None)
    if item is None:
        raise ErroServico("Item não encontrado.")
    if item["quantidade"] == quantidade:
        return
    _, afetados = executar_com_auditoria(
        "UPDATE itens_pedido SET quantidade = %s WHERE id_item_pedido = %s AND id_pedido = %s",
        (quantidade, id_item, id_pedido),
        "pedido.item_atualizado",
        "pedido",
        id_pedido,
        str(id_item),
    )
    if afetados == 0:
        raise ErroServico("Item não encontrado.")


def remover_item_pedido(id_pedido, id_item):
    pedido = obter_pedido(id_pedido)
    if pedido["situacao"] != "aberto":
        raise ErroServico("Essa comanda já foi fechada.")
    _, afetados = executar_com_auditoria(
        "DELETE FROM itens_pedido WHERE id_item_pedido = %s AND id_pedido = %s",
        (id_item, id_pedido),
        "pedido.item_removido",
        "pedido",
        id_pedido,
        str(id_item),
    )
    if afetados == 0:
        raise ErroServico("Item não encontrado.")


def fechar_pedido(id_pedido, forma_pagamento, texto_valor_recebido=None):
    if forma_pagamento not in {"dinheiro", "pix", "debito", "credito"}:
        raise ErroServico("Selecione uma forma de pagamento.")

    banco = obter_banco()
    cursor = banco.cursor(dictionary=True)
    try:
        banco.start_transaction()
        cursor.execute(
            """
            SELECT o.id_pedido, o.situacao, c.numero_cartao
            FROM pedidos o
            JOIN cartoes_comanda c ON c.id_cartao = o.id_cartao
            WHERE o.id_pedido = %s
            FOR UPDATE
            """,
            (id_pedido,),
        )
        pedido = cursor.fetchone()
        if not pedido:
            raise ErroServico("Comanda não encontrada.")
        if pedido["situacao"] != "aberto":
            raise ErroServico("Essa comanda já foi fechada.")

        cursor.execute(
            "SELECT COALESCE(SUM(quantidade * preco_unitario), 0) AS total FROM itens_pedido WHERE id_pedido = %s",
            (id_pedido,),
        )
        total = Decimal(str(cursor.fetchone()["total"]))
        if total <= 0:
            raise ErroServico("Adicione pelo menos um produto antes de fechar a comanda.")

        valor_recebido = None
        troco = None
        if forma_pagamento == "dinheiro":
            valor_recebido = converter_valor(texto_valor_recebido)
            if valor_recebido is None or valor_recebido < total:
                raise ErroServico("O valor recebido deve ser igual ou maior que o total.")
            troco = valor_recebido - total

        cursor.execute(
            """
            INSERT INTO vendas
                (id_pedido, numero_cartao_historico, valor_total, forma_pagamento, valor_recebido, troco)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (id_pedido, pedido["numero_cartao"], total, forma_pagamento, valor_recebido, troco),
        )
        id_venda = cursor.lastrowid
        cursor.execute(
            "UPDATE pedidos SET situacao = 'fechado', fechado_em = CURRENT_TIMESTAMP WHERE id_pedido = %s",
            (id_pedido,),
        )
        registrar_auditoria(cursor, "pedido.fechado", "pedido", id_pedido, forma_pagamento)
        banco.commit()
        return id_venda
    except mysql.connector.IntegrityError as erro:
        banco.rollback()
        raise ErroServico("O pagamento dessa comanda já foi registrado.") from erro
    except Exception:
        banco.rollback()
        raise
    finally:
        cursor.close()


def listar_vendas(busca="", forma_pagamento="todos", data_inicial="", data_final=""):
    for valor in (data_inicial, data_final):
        if valor:
            try:
                datetime.strptime(valor, "%Y-%m-%d")
            except ValueError as erro:
                raise ErroServico("Informe datas válidas no formato AAAA-MM-DD.") from erro
    if data_inicial and data_final and data_inicial > data_final:
        raise ErroServico("A dados inicial não pode ser posterior à dados final.")
    condicoes = ["1 = 1"]
    parametros = []
    digitos = "".join(caractere for caractere in busca if caractere.isdigit())
    if digitos:
        condicoes.append("(s.numero_cartao_historico LIKE %s OR CAST(s.id_venda AS CHAR) LIKE %s)")
        parametros.extend((f"%{digitos}%", f"%{digitos}%"))
    if forma_pagamento in {"dinheiro", "pix", "debito", "credito"}:
        condicoes.append("s.forma_pagamento = %s")
        parametros.append(forma_pagamento)
    if data_inicial:
        condicoes.append("DATE(s.vendido_em) >= %s")
        parametros.append(data_inicial)
    if data_final:
        condicoes.append("DATE(s.vendido_em) <= %s")
        parametros.append(data_final)

    return buscar_todos(
        f"""
        SELECT s.id_venda, s.id_pedido, s.numero_cartao_historico, s.valor_total,
               s.forma_pagamento, s.vendido_em, o.identificacao_atendimento
        FROM vendas s
        JOIN pedidos o ON o.id_pedido = s.id_pedido
        WHERE {' AND '.join(condicoes)}
        ORDER BY s.vendido_em DESC
        """,
        tuple(parametros),
    )


def obter_venda(id_venda):
    venda = buscar_um(
        """
        SELECT s.*, o.identificacao_atendimento, o.aberto_em, o.fechado_em
        FROM vendas s
        JOIN pedidos o ON o.id_pedido = s.id_pedido
        WHERE s.id_venda = %s
        """,
        (id_venda,),
    )
    if not venda:
        raise ErroServico("Venda não encontrada.")
    venda["itens"] = buscar_todos(
        """
        SELECT nome_produto_historico, nome_categoria_historico,
               preco_unitario, quantidade, quantidade * preco_unitario AS total_item
        FROM itens_pedido
        WHERE id_pedido = %s
        ORDER BY id_item_pedido
        """,
        (venda["id_pedido"],),
    )
    return venda


def obter_resumo(periodo):
    dados_periodo = obter_intervalo_periodo(periodo)
    parametros = (dados_periodo["inicio"], dados_periodo["fim"])
    indicadores = buscar_um(
        """
        SELECT COUNT(*) AS vendas_concluidas,
               COALESCE(SUM(valor_total), 0) AS faturamento,
               COALESCE(AVG(valor_total), 0) AS valor_medio_venda
        FROM vendas
        WHERE vendido_em >= %s AND vendido_em < %s
        """,
        parametros,
    )
    anterior = buscar_um(
        """
        SELECT COALESCE(SUM(valor_total), 0) AS faturamento
        FROM vendas
        WHERE vendido_em >= %s AND vendido_em < %s
        """,
        (dados_periodo["inicio_anterior"], dados_periodo["inicio"]),
    )

    if dados_periodo["periodo"] == "diario":
        consulta_evolucao = """
            SELECT CONCAT(LPAD(hora_venda, 2, '0'), 'h') AS rotulo, vendas, faturamento
            FROM (
                SELECT HOUR(vendido_em) AS hora_venda,
                       COUNT(*) AS vendas, SUM(valor_total) AS faturamento
                FROM vendas
                WHERE vendido_em >= %s AND vendido_em < %s
                GROUP BY HOUR(vendido_em)
            ) AS vendas_por_hora
            ORDER BY hora_venda
        """
    else:
        consulta_evolucao = """
            SELECT DATE_FORMAT(data_venda, '%d/%m') AS rotulo, vendas, faturamento
            FROM (
                SELECT DATE(vendido_em) AS data_venda,
                       COUNT(*) AS vendas, SUM(valor_total) AS faturamento
                FROM vendas
                WHERE vendido_em >= %s AND vendido_em < %s
                GROUP BY DATE(vendido_em)
            ) AS vendas_diarias
            ORDER BY data_venda
        """

    evolucao = buscar_todos(consulta_evolucao, parametros)
    maximo = max((Decimal(str(registro["faturamento"])) for registro in evolucao), default=Decimal("0"))
    for registro in evolucao:
        valor = Decimal(str(registro["faturamento"]))
        registro["altura"] = int((valor / maximo) * 100) if maximo > 0 else 0

    formas_pagamento = buscar_todos(
        """
        SELECT forma_pagamento, COUNT(*) AS vendas, SUM(valor_total) AS faturamento
        FROM vendas
        WHERE vendido_em >= %s AND vendido_em < %s
        GROUP BY forma_pagamento
        ORDER BY faturamento DESC
        """,
        parametros,
    )
    produtos_mais_vendidos = buscar_todos(
        """
        SELECT i.nome_produto_historico AS nome, SUM(i.quantidade) AS quantidade,
               SUM(i.quantidade * i.preco_unitario) AS faturamento
        FROM vendas s
        JOIN itens_pedido i ON i.id_pedido = s.id_pedido
        WHERE s.vendido_em >= %s AND s.vendido_em < %s
        GROUP BY i.nome_produto_historico
        ORDER BY quantidade DESC, faturamento DESC
        LIMIT 5
        """,
        parametros,
    )

    faturamento = Decimal(str(indicadores["faturamento"]))
    faturamento_anterior = Decimal(str(anterior["faturamento"]))
    comparacao = None
    if faturamento_anterior > 0:
        comparacao = ((faturamento - faturamento_anterior) / faturamento_anterior) * 100

    return {
        "periodo": dados_periodo["periodo"],
        "rotulo": dados_periodo["rotulo"],
        "indicadores": indicadores,
        "comparacao": comparacao,
        "evolucao": evolucao,
        "formas_pagamento": formas_pagamento,
        "produtos_mais_vendidos": produtos_mais_vendidos,
    }


def obter_estabelecimento():
    return buscar_um("SELECT * FROM estabelecimentos WHERE id_estabelecimento = 1")


def atualizar_estabelecimento(nome, correio, tipo_estabelecimento):
    nome = " ".join(str(nome or "").strip().split())
    correio = str(correio or "").strip().lower()
    tipo_estabelecimento = " ".join(str(tipo_estabelecimento or "").strip().split())
    if (not 2 <= len(nome) <= 120 or "@" not in correio or "." not in correio
            or len(correio) > 150 or not 2 <= len(tipo_estabelecimento) <= 100):
        raise ErroServico("Revise os dados do estabelecimento.")
    executar_com_auditoria(
        """
        UPDATE estabelecimentos
        SET nome = %s, correio = %s, tipo_estabelecimento = %s
        WHERE id_estabelecimento = 1
        """,
        (nome, correio, tipo_estabelecimento),
        "estabelecimento.atualizado",
        "estabelecimento",
        1,
        nome,
    )
