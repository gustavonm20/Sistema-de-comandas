# Banco de dados — FluxoPag

O projeto utiliza **MySQL 8** como banco relacional. O schema oficial está em [`database/schema.sql`](../database/schema.sql) e foi pensado para suportar as telas e fluxos definidos no Figma: produtos, comandas, pagamento, histórico e resumos por dia, semana e mês.

A nomenclatura das tabelas, colunas, views, índices e valores de domínio foi padronizada em **português** para manter o banco coerente com o projeto e facilitar a leitura durante o desenvolvimento.

Esta documentação deve evoluir junto com o `schema.sql`, registrando as decisões de modelagem antes das próximas integrações com o backend.

## Estrutura atual

### `categorias`
Classifica os produtos. O nome da categoria é único para evitar duplicidades.

### `produtos`
Armazena nome, preço atual, categoria e status ativo/inativo. Produtos desativados continuam existindo para preservar referências históricas.

### `comandas`
Representa as comandas físicas do estabelecimento. O número possui quatro dígitos e é reutilizável após o fechamento de um atendimento.

### `pedidos`
Representa cada utilização de uma comanda física. Uma mesma comanda pode gerar muitos pedidos ao longo do tempo, mas somente um deles pode permanecer aberto por vez.

A coluna gerada `comanda_aberta_id` combinada com `UNIQUE` garante essa regra diretamente no banco: quando o pedido está aberto, ela recebe o `comanda_id`; quando fecha, passa a `NULL` e o número pode ser reutilizado.

### `itens_pedido`
Liga produtos aos pedidos e registra quantidade, preço unitário no momento do consumo e observações. O preço é copiado para o item para que alterações futuras no catálogo não modifiquem vendas antigas.

### `vendas`
Registra o fechamento financeiro de um pedido, incluindo valor total, forma de pagamento e data/hora. Cada pedido pode gerar no máximo uma venda.

## Views

As views funcionam como consultas reutilizáveis que simplificam a futura API e correspondem às principais telas do Figma.

- `vw_produtos`: catálogo com categoria e status.
- `vw_comandas_abertas`: comandas abertas e total atual.
- `vw_resumo_pedido`: itens, subtotais e total de uma comanda.
- `vw_historico_vendas`: histórico de vendas com número da comanda e forma de pagamento legível.
- `vw_resumo_diario`: quantidade de vendas, faturamento e ticket médio por dia.
- `vw_resumo_semanal`: consolidação semanal.
- `vw_resumo_mensal`: consolidação mensal.

## Recursos SQL utilizados

### `PRIMARY KEY` e `AUTO_INCREMENT`
Fornecem uma identidade interna estável para cada registro e geram os IDs automaticamente.

### `FOREIGN KEY`
Mantém integridade referencial entre categorias, produtos, comandas, pedidos, itens e vendas.

### `CHECK`
Impõe regras como preço não negativo, quantidade maior que zero e número da comanda com exatamente quatro dígitos numéricos.

### `ENUM`
Restringe estados e formas de pagamento aos valores aceitos pelo domínio. No schema atual, os pedidos usam `aberto` e `fechado`; as vendas usam `dinheiro`, `credito`, `debito` e `pix`.

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
3. Execute o script completo em um banco novo.
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

## Atenção sobre bancos já criados

A alteração dos nomes para português muda a estrutura lógica do schema. `CREATE TABLE IF NOT EXISTS` não renomeia tabelas antigas automaticamente.

Enquanto o banco estiver apenas em desenvolvimento e sem dados importantes, a opção mais simples é criar um schema limpo usando o arquivo atualizado. Quando o projeto possuir dados persistentes importantes, mudanças desse tipo deverão ser feitas por **migrations**, sem apagar o banco.

## Próximas evoluções

- transação atômica para pagamento e fechamento da comanda;
- abertura e fechamento diário do caixa;
- controle de estoque e movimentações;
- estabelecimento e autenticação;
- cancelamentos, estornos e auditoria;
- migrations para evolução controlada do schema;
- backup e restauração.
