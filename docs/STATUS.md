# Estado do projeto e evidências

[Índice](README.md) · [Testes](TESTING.md)

Revisão: **18/09/2026**. Base inicialmente auditada: commit `9c0317fe190917e12f1966d1b454f266986e8a1d`. A consolidação foi integrada à `main` pela [PR #25](https://github.com/gustavonm20/Sistema-de-comandas/pull/25), no commit `1a7830ef6bcdb8b5047fe3d760433ec8bb15d2b4`. A integração disponibiliza os fontes; não encerra requisitos ainda pendentes.

## Como ler os estados

- **Verificado:** existe uma execução identificada para o comportamento descrito.
- **Implementado, por verificar:** há código, mas falta a execução pertinente, para o cenário em questão.
- **Parcial:** há código ou design, porém requisitos relevantes ainda não são atendidos.
- **Só design:** existe representação visual sem comportamento equivalente comprovado no aplicativo.
- **Planejado:** consta do escopo ou backlog, sem implementação localizada.

Um teste estrutural, um mock ou um teste do terminal JSON não comprova integração MySQL. A [verificação](TESTING.md) registra essa separação.

| Recurso | Estado do código | Evidência principal | Execução | Design / issue |
| --- | --- | --- | --- | --- |
| Protótipo inicial | Artefato histórico preservado; catálogo em memória, outros menus são esboços | [protótipo-inicial.py](../protótipo-inicial.py) | Sintaxe e abertura/saída do menu | Treino anterior |
| Evolução terminal JSON | Histórico; lógica e persistência de arquivo | [legacy/terminal-json](../legacy/terminal-json/README.md) | 6 testes locais aprovados | Não é a aplicação MySQL |
| Conversão de dinheiro e períodos | Verificado nos casos da suíte local | [utils.py](../utils.py), [test_utils.py](../tests/test_utils.py) | 11 testes unitários | #17 |
| Catálogo persistente | Verificado nos cenários da suíte MySQL; revisão humana pendente | `validate_product`, `create_product`, `list_products`, `update_product`, `set_product_status` em [services.py](../services.py) | CRUD, filtros e reconexão aprovados em MySQL real | Hi-fi e low-fi / #11 |
| Cartões e abertura de comandas | Parcial; valida operação, disponibilidade e número | `create_command_card`, `create_order`; `UNIQUE(open_card_id)` | Número, operação requerida e exclusividade sequencial verificados | #12 |
| Itens e preço histórico | Parcial; snapshots e bloqueio de produto inativo; concorrência pendente | `add_order_item`, `update_order_item`, `remove_order_item`, [schema](../database/schema.sql) | Itens, quantidade, inatividade e snapshots verificados em MySQL | #11, #12, #21 |
| Fechamento e histórico | Parcial; transação, venda única, troco e consultas presentes | `close_order`, `list_sales`, `get_sale` | Rollback, venda única sequencial, troco e reutilização verificados | #13, #21 |
| Processamento financeiro externo | Fora do escopo atual; exige nova decisão | Não há provedor, webhook ou confirmação bancária | Não se aplica | Sem entrega afirmada |
| Dados do estabelecimento | Implementado; alteração dos dados ainda sem teste específico | `get_establishment`, `update_establishment`, [account.html](../templates/account.html) | Template e GET com MySQL testados; POST da conta não exercitado | Conta hi-fi / #10, #24 |
| Login, senha e saída | Só design / planejado no código | Não há rotas de autenticação | Não implementado | Controles visuais no Figma / #24 |
| Abertura e conferência do caixa | Parcial; valores, divergência e bloqueio presentes; corridas pendentes | `open_operation`, `close_operation`, `daily_operations` | Caixa, divergência e bloqueio sequencial aprovados em MySQL | Hi-fi existe, low-fi específico falta / #5–#7, #14 |
| Resumos diário, semanal e mensal | Parcial; páginas por parâmetro e SQL presentes; não selecionam operação encerrada | `/reports?period=daily`, `weekly`, `monthly`, `get_report` | Limites de calendário e consultas dos três períodos testados | Três frames hi-fi / #8, #15 |
| Layout, tema e navegação | Implementado; revisão visual e de acessibilidade parcial | [templates](../templates/), [CSS](../static/css/style.css), [JS](../static/js/main.js) | Templates, assets e 15 GETs com MySQL testados; sem navegação completa no navegador | #16 |
| Schema e views | Inicialização e consultas verificadas em MySQL real | [database/schema.sql](../database/schema.sql), nove tabelas e sete views | MySQL 8.4.11: inicialização, constraints, FKs e sete views aprovadas | #10, #19 |
| Auditoria básica | Implementada; ator fixo `local-admin` | `record_audit`, `audit_logs` | Rollback com falha na auditoria testado; não identifica usuário autenticado | #24 |
| Migrations e estoque | Planejados | Nenhum executor de migrations ou saldo de estoque | Não implementados | #19, #20 |
| CI | Workflow executado com sucesso | [verify.yml](../.github/workflows/verify.yml) | Resultado remoto registrado em [TESTING.md](TESTING.md) | #17 |

## Pendências que impedem afirmar maturidade operacional

1. Revisar os fluxos interativos e os POSTs ainda não exercitados, além do setup no Windows. A integração MySQL já passou na [execução 35213699602](https://github.com/gustavonm20/Sistema-de-comandas/actions/runs/35213699602).
2. Evitar disputa entre edição de itens e fechamento, e entre abertura de comanda e encerramento da operação (#21, #14).
3. Definir o comportamento quando o preço muda entre duas inclusões do mesmo produto: o código conserva a primeira linha e o primeiro preço (#1, #12).
4. Criar migrations sem perda de dados (#19), autenticação e CSRF (#24).
5. Alinhar resumo por operação, períodos comparados e seleção de datas (#15).
6. Completar as conexões de caixa e os wireframes correspondentes no Figma (#5–#9).
