"""Nomes antigos usados somente para ler instalações anteriores do FluxoPag.

Estas grafias são contratos de compatibilidade. Não são usadas pelo sistema novo.
"""

TABELAS_ANTIGAS = [('establishments', 'estabelecimentos', {'establishment_id': 'id_estabelecimento', 'name': 'nome', 'email': 'correio', 'business_type': 'tipo_estabelecimento', 'created_at': 'criado_em', 'updated_at': 'atualizado_em'}, []), ('categories', 'categorias', {'category_id': 'id_categoria', 'name': 'nome', 'active': 'ativo', 'created_at': 'criado_em', 'updated_at': 'atualizado_em'}, []), ('products', 'produtos', {'product_id': 'id_produto', 'name': 'nome', 'normalized_name': 'nome_normalizado', 'price': 'preco', 'category_id': 'id_categoria', 'active': 'ativo', 'created_at': 'criado_em', 'updated_at': 'atualizado_em'}, []), ('command_cards', 'cartoes_comanda', {'card_id': 'id_cartao', 'card_number': 'numero_cartao', 'active': 'ativo', 'created_at': 'criado_em', 'updated_at': 'atualizado_em'}, []), ('daily_operations', 'operacoes_diarias', {'operation_id': 'id_operacao', 'status': 'situacao', 'opening_cash': 'caixa_inicial', 'expected_cash': 'caixa_esperado', 'counted_cash': 'caixa_contado', 'difference_amount': 'valor_diferenca', 'discrepancy_note': 'justificativa_diferenca', 'opened_at': 'aberto_em', 'closed_at': 'fechado_em'}, ['open_operation_marker']), ('orders', 'pedidos', {'order_id': 'id_pedido', 'card_id': 'id_cartao', 'operation_id': 'id_operacao', 'service_type': 'tipo_atendimento', 'service_label': 'identificacao_atendimento', 'note': 'observacao', 'status': 'situacao', 'opened_at': 'aberto_em', 'closed_at': 'fechado_em'}, ['open_card_id']), ('order_items', 'itens_pedido', {'order_item_id': 'id_item_pedido', 'order_id': 'id_pedido', 'product_id': 'id_produto', 'notes': 'observacoes', 'product_name_snapshot': 'nome_produto_historico', 'category_name_snapshot': 'nome_categoria_historico', 'unit_price': 'preco_unitario', 'quantity': 'quantidade', 'created_at': 'criado_em', 'updated_at': 'atualizado_em'}, []), ('sales', 'vendas', {'sale_id': 'id_venda', 'order_id': 'id_pedido', 'card_number_snapshot': 'numero_cartao_historico', 'total_amount': 'valor_total', 'payment_method': 'forma_pagamento', 'cash_received': 'valor_recebido', 'change_amount': 'troco', 'sold_at': 'vendido_em'}, []), ('audit_logs', 'registros_auditoria', {'log_id': 'id_registro', 'actor': 'responsavel', 'action': 'acao', 'entity_type': 'tipo_entidade', 'entity_id': 'id_entidade', 'detail': 'detalhe', 'created_at': 'criado_em'}, [])]

VALORES_ANTIGOS = {
    "situacao": {"open": "aberto", "closed": "fechado"},
    "tipo_atendimento": {"table": "mesa", "counter": "balcao", "pickup": "retirada"},
    "forma_pagamento": {"cash": "dinheiro", "pix": "pix", "debit": "debito", "credit": "credito"},
    "responsavel": {"local-admin": "administrador-local"},
}

VALORES_ANTIGOS["acao"] = {'establishment.updated': 'estabelecimento.atualizado', 'operation.closed': 'operacao.fechado', 'operation.opened': 'operacao.aberto', 'order.closed': 'pedido.fechado', 'order.item_added': 'pedido.item_adicionado', 'order.item_removed': 'pedido.item_removido', 'order.item_updated': 'pedido.item_atualizado', 'order.opened': 'pedido.aberto', 'product.activated': 'produto.activated', 'product.created': 'produto.criado', 'product.deactivated': 'produto.deactivated', 'product.updated': 'produto.atualizado'}
VALORES_ANTIGOS["tipo_entidade"] = {'product': 'produto', 'order': 'pedido', 'daily_operation': 'operacao_diaria', 'establishment': 'estabelecimento', 'command_card': 'cartao_comanda'}

def converter_valor_antigo(coluna, valor):
    return VALORES_ANTIGOS.get(coluna, {}).get(valor, valor)
