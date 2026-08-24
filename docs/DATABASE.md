# Banco de dados — FluxoPag

O projeto utiliza **MySQL 8** como banco relacional. O schema oficial está em [`database/schema.sql`](../database/schema.sql) e foi pensado para suportar as telas e fluxos definidos no Figma: produtos, comandas, pagamento, histórico e resumos por dia, semana e mês.

## Estrutura atual

### `categories`
Classifica os produtos. O nome da categoria é único para evitar duplicidades.

### `products`
Armazena nome, preço atual, categoria e status ativo/inativo. Produtos desativados continuam existindo para preservar referências históricas.

### `command_cards`
Representa as comandas físicas do estabelecimento. O número possui quatro dígitos e é reutilizável após o fechamento de um atendimento.

### `orders`
Representa cada utilização de uma comanda física. Uma mesma comanda pode gerar muitos pedidos ao longo do tempo, mas somente um deles pode permanecer aberto por vez.

A coluna gerada `open_card_id` combinada com `UNIQUE` garante essa regra diretamente no banco: quando o pedido está aberto, ela recebe o `card_id`; quando fecha, passa a `NULL` e o número pode ser reutilizado.

### `order_items`
Liga produtos aos pedidos e registra quantidade, preço unitário no momento do consumo e observações. O preço é copiado para o item para que alterações futuras no catálogo não modifiquem vendas antigas.

### `sales`
Registra o fechamento financeiro de um pedido, incluindo total, forma de pagamento e data/hora. Cada pedido pode gerar no máximo uma venda.

## Views

As views funcionam como consultas reutilizáveis que simplificam a futura API e correspondem às principais telas do Figma.

- `vw_products`: catálogo com categoria e status.
- `vw_open_orders`: comandas abertas e total atual.
- `vw_order_summary`: itens, subtotais e total de uma comanda.
- `vw_sales_history`: histórico de vendas com número da comanda e forma de pagamento legível.
- `vw_daily_summary`: quantidade de vendas, faturamento e ticket médio por dia.
- `vw_weekly_summary`: consolidação semanal.
- `vw_monthly_summary`: consolidação mensal.

## Recursos SQL utilizados

### `PRIMARY KEY` e `AUTO_INCREMENT`
Fornecem uma identidade interna estável para cada registro e geram os IDs automaticamente.

### `FOREIGN KEY`
Mantém integridade referencial entre categorias, produtos, comandas, itens e vendas.

### `CHECK`
Impõe regras como preço não negativo, quantidade maior que zero e número da comanda com exatamente quatro dígitos numéricos.

### `ENUM`
Restringe estados e formas de pagamento aos valores aceitos pelo domínio.

### Coluna gerada + `UNIQUE`
Impede que uma mesma comanda física esteja aberta em dois atendimentos simultâneos.

### `VIEW`
Salva consultas complexas para reutilização sem duplicar a lógica em vários pontos da aplicação.

### Window function
A expressão `SUM(...) OVER (PARTITION BY ...)` calcula o total da comanda sem eliminar as linhas individuais dos produtos.

### Índices
Foram adicionados índices nos campos usados com frequência em filtros e relacionamentos, como status de pedidos, data de venda, forma de pagamento e categoria de produto.

## Executando no MySQL Workbench

1. Abra o MySQL Workbench e conecte-se ao MySQL 8.
2. Abra `database/schema.sql`.
3. Execute o script completo.
4. Atualize a área **Schemas**.
5. Verifique as tabelas com:

```sql
SHOW TABLES;
```

Para exibir também as views:

```sql
SHOW FULL TABLES;
```

## Formato de data e hora

O banco mantém valores `DATETIME` de forma nativa. A apresentação usada nas views segue o padrão definido para o projeto:

```text
19:51  01/01/2026
```

Isso é feito com `DATE_FORMAT`, preservando o tipo correto no armazenamento.

## Próximas evoluções

- transação atômica para pagamento e fechamento da comanda;
- abertura e fechamento diário do caixa;
- controle de estoque e movimentações;
- estabelecimento e autenticação;
- cancelamentos, estornos e auditoria;
- migrations para evolução controlada do schema;
- backup e restauração.
