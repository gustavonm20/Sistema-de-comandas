# Histórico de mudanças

## 19/09/2026 — Projeto em português

- Tradução dos identificadores próprios, rotas, campos, arquivos, interface e documentação.
- MySQL mantido, com valores monetários em `Decimal` e `DECIMAL`.
- Cópia explícita do banco anterior para a estrutura em português, sem alterar a origem.
- Leitura dos dados JSON antigos no protótipo de terminal.
- Testes de conversão e formulários, e rotina de verificação com os novos caminhos.
- Histórico Git preservado; somente novos registros de alteração.


Este registro descreve mudanças verificáveis, sem criar números de versão ou lançamentos retroativos. A história completa permanece nos registros de alteração e solicitações de integração.

## Não lançado — 18/09/2026

- Finalização dos guias para a `main`: instalação sem troca para ramo temporária, matriz de situação, planejamento e ligações das tarefas atualizados.
- Política do Kanban reconciliada com a integração da solicitação de integração #25, preservando pendências e critérios das tarefas.
- integração contínua mantida em solicitações de integração e na `main`, removendo a referência temporária de push para a antiga ramo de consolidação.

## Não lançado — 17/09/2026

Consolidação integrada à `main` pela [solicitação de integração #25](https://github.com/gustavonm20/Sistema-de-comandas/pull/25), no registro de alteração `1a7830ef6bcdb8b5047fe3d760433ec8bb15d2b4`:

- Fontes de `FluxoPag-Flask-MySQL.zip` extraídos e consolidados: servidor Flask, modelos, CSS, JavaScript, recursos, estrutura e dependências.
- Evolução do terminal JSON recuperada em `legado/terminal-json/`; protótipo inicial e estrutura anterior preservadas.
- Configuração `.env` funcional, inicialização protegida de banco vazio, dados fictícios opcionais e tratamento de indisponibilidade do banco.
- Compatibilidade de `id_item_pedido`, índices, cópias históricas, limites de validação e cálculos de calendário revisados.
- Agregações dos resumos corrigidas para MySQL com `ONLY_FULL_GROUP_BY`.
- integração contínua com MySQL real: 36 testes da aplicação e seis históricos aprovados no [registro de alteração 2adc690](https://github.com/gustavonm20/Sistema-de-comandas/commit/2adc6900b09f988ef975e285207b57dcab842e10).
- README, guias técnicos, ERD, evidências, origem dos arquivos, projeto visual, planejamento e orientações de contribuição reconciliados.
- Logo original e prévia autêntica do Figma; link do protótipo separado do arquivo de projeto visual.
- Tarefas existentes revisadas e #24 criada para acesso/autenticação/CSRF. Nenhuma tarefa de implementação encerrada por causa desta documentação.

Autenticação, proteção CSRF, migrações, estoque e garantias completas sob concorrência **não** fazem parte das funcionalidades concluídas nesta entrega. A configuração nativa pendente do Projects e metadados está registrada em [QUADRO_TAREFAS.md](documentacao/QUADRO_TAREFAS.md).

## Histórico confirmado

| Data de integração | Mudança verificável |
| --- | --- |
| 24/08/2026 | [solicitação de integração #22](https://github.com/gustavonm20/Sistema-de-comandas/pull/22): fundação MySQL. |
| 24/08/2026 | [solicitação de integração #23](https://github.com/gustavonm20/Sistema-de-comandas/pull/23): tradução SQL para português naquele momento. A estrutura da base auditada posterior voltou a nomes ingleses; esta consolidação segue o arquivo encontrado. |
| 04/08/2026 | [solicitação de integração #18](https://github.com/gustavonm20/Sistema-de-comandas/pull/18): organização de documentação e planejamento. |

A evolução terminal → Figma → modelagem → web é descrita na [visão do produto](documentacao/PRODUTO.md), sem atribuir datas não comprovadas às fases de criação.
