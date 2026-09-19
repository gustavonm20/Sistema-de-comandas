# Histórico de mudanças

Este registro descreve mudanças verificáveis, sem criar números de versão ou lançamentos retroativos. A história completa permanece nos commits e pull requests.

## Não lançado — 17/09/2026

Entrega proposta na branch `chore/consolidar-fluxopag`, ainda sujeita a revisão:

- Fontes de `FluxoPag-Flask-MySQL.zip` extraídos e consolidados: backend Flask, templates, CSS, JavaScript, assets, schema e dependências.
- Evolução do terminal JSON recuperada em `legacy/terminal-json/`; protótipo inicial e schema anterior preservados.
- Configuração `.env` funcional, inicialização protegida de banco vazio, dados fictícios opcionais e tratamento de indisponibilidade do banco.
- Compatibilidade de `order_item_id`, índices, snapshots, limites de validação e cálculos de calendário revisados.
- Agregações dos resumos corrigidas para MySQL com `ONLY_FULL_GROUP_BY`.
- CI com MySQL real: 36 testes da aplicação e seis históricos aprovados no [commit 2adc690](https://github.com/gustavonm20/Sistema-de-comandas/commit/2adc6900b09f988ef975e285207b57dcab842e10).
- README, guias técnicos, ERD, evidências, origem dos arquivos, design, roadmap e orientações de contribuição reconciliados.
- Logo original e prévia autêntica do Figma; link do protótipo separado do arquivo de design.
- Issues existentes revisadas e #24 criada para acesso/autenticação/CSRF. Nenhuma issue de implementação encerrada por causa desta documentação.

Login, proteção CSRF, migrations, estoque e garantias completas sob concorrência **não** fazem parte das funcionalidades concluídas nesta entrega. A configuração nativa pendente do Projects e metadados está registrada em [KANBAN.md](docs/KANBAN.md).

## Histórico confirmado

| Data de integração | Mudança verificável |
| --- | --- |
| 24/08/2026 | [PR #22](https://github.com/gustavonm20/Sistema-de-comandas/pull/22): fundação MySQL. |
| 24/08/2026 | [PR #23](https://github.com/gustavonm20/Sistema-de-comandas/pull/23): tradução SQL para português naquele momento. O schema da base auditada posterior voltou a nomes ingleses; esta consolidação segue o arquivo encontrado. |
| 04/08/2026 | [PR #18](https://github.com/gustavonm20/Sistema-de-comandas/pull/18): organização de documentação e roadmap. |

A evolução terminal → Figma → modelagem → web é descrita na [visão do produto](docs/PRODUCT.md), sem atribuir datas não comprovadas às fases de criação.
