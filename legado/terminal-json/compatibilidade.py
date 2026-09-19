"""Leitura das chaves usadas pela versão anterior do protótipo JSON."""

CHAVES_ANTIGAS = {'products': 'produtos', 'open_orders': 'pedidos_abertos', 'sales': 'vendas', 'cash_sessions': 'sessoes_caixa', 'product_id': 'id_produto', 'name': 'nome', 'price_cents': 'preco_centavos', 'category': 'categoria', 'active': 'ativo', 'product_name': 'nome_produto', 'unit_price_cents': 'preco_unitario_centavos', 'quantity': 'quantidade', 'order_number': 'numero_comanda', 'opened_at': 'aberto_em', 'items': 'itens', 'sale_id': 'id_venda', 'total_cents': 'total_centavos', 'payment_method': 'forma_pagamento', 'closed_at': 'fechado_em', 'cash_session_id': 'id_sessao_caixa', 'session_id': 'id_sessao', 'opening_balance_cents': 'saldo_inicial_centavos', 'expected_cash_cents': 'caixa_esperado_centavos', 'actual_cash_cents': 'caixa_contado_centavos', 'difference_cents': 'diferenca_centavos'}

def converter_dados_antigos(dados):
    if isinstance(dados, list):
        return [converter_dados_antigos(item) for item in dados]
    if isinstance(dados, dict):
        convertido = {}
        for chave, valor in dados.items():
            nova_chave = CHAVES_ANTIGAS.get(chave, chave)
            if nova_chave in convertido:
                raise ValueError("O arquivo mistura chaves antigas e novas. Nenhum dado foi salvo.")
            convertido[nova_chave] = converter_dados_antigos(valor)
        return convertido
    return dados
