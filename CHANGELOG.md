# Changelog

Todas as mudanças relevantes do projeto serão registradas neste arquivo.

O formato é inspirado em *Keep a Changelog* e o projeto pretende adotar versionamento semântico quando a aplicação possuir releases.

## [Unreleased]

### Adicionado

- protótipo didático em Python executado no terminal;
- menu de produtos com cadastro, listagem, pesquisa, edição e desativação;
- planejamento do fluxo de comandas, histórico e resumos;
- protótipo hi-fi do FluxoPag no Figma;
- telas de Dashboard, Produtos, Comandas, Nova comanda, Detalhes, Pagamento e Histórico;
- conta autenticada representando o estabelecimento;
- estados de dia não iniciado e dia em andamento;
- resumos diário, semanal e mensal;
- parte dos wireframes low-fi;
- documentação de regras de negócio;
- roadmap com issues de design, backend, frontend, MVP e qualidade;
- templates de issue e pull request;
- schema inicial do MySQL em `database/schema.sql`;
- tabelas `categories`, `products`, `command_cards`, `orders`, `order_items` e `sales`;
- constraints de integridade para preços, quantidades, estados e números de comandas;
- proteção para impedir dois atendimentos abertos na mesma comanda física;
- índices iniciais para consultas de produtos, pedidos e vendas;
- views para catálogo, comandas abertas, detalhes da comanda e histórico de vendas;
- views para resumos diário, semanal e mensal;
- documentação específica da modelagem em `docs/DATABASE.md`.

### Alterado

- banco planejado alterado de SQLite para MySQL 8;
- documentação deixou de fixar Flask + SQLite como arquitetura definitiva;
- roadmap atualizado para refletir o início da fundação técnica;
- Kanban documentado com a issue #10 em andamento;
- cadastro de produtos de exemplo passou a localizar categorias pelo nome em vez de depender de IDs fixos;
- datas permanecem armazenadas como `DATETIME` e são formatadas nas views para `HH:MM  DD/MM/AAAA`.

### Planejado

- integração Python ↔ MySQL;
- migrations versionadas;
- transação atômica para fechamento de comanda e registro da venda;
- abertura de caixa com valor inicial;
- bloqueio do fechamento com comandas abertas;
- confirmação de encerramento;
- conferência e fechamento de caixa;
- comparação entre períodos;
- controle de estoque e movimentações;
- conclusão e organização do low-fi e hi-fi;
- testes automatizados e GitHub Actions;
- backup e restauração.
