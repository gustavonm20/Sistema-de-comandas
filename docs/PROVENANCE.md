# Origem dos arquivos e decisões de integração

[Índice](README.md) · [Mudanças](../CHANGELOG.md)

Revisão em 17/09/2026. A referência inicial do GitHub foi `main` em `9c0317fe190917e12f1966d1b454f266986e8a1d`. Foram comparados os arquivos dessa base, branches relevantes, PRs #18, #22 e #23 já integradas, issues abertas/fechadas e os artefatos acessíveis. Nenhum commit anterior foi reescrito.

## Fontes examinadas

| Fonte | Conteúdo observado | Destino / decisão |
| --- | --- | --- |
| Repositório na base auditada | Protótipo Python, schema SQL e documentos; sem aplicação Flask completa | Histórico preservado; documentos reconciliados com o código |
| `FluxoPag-Flask-MySQL.zip` | Quatro módulos Python, 15 templates, CSS, JS, imagens, schema, dependências e testes iniciais | Fonte web extraída na raiz, revisada e corrigida |
| `FluxoPag_Prototipo_Final.zip` | Evolução de terminal com serviços, persistência JSON e seis testes | Preservado em `legacy/terminal-json/`, sem alimentar a web |
| Fonte anterior do protótipo de interface, commit `ff28c1604811233331926f2884e99b8f75b456f3` | React/Next/vinext, Tailwind e Drizzle, fora da stack acordada; marca e ícones coincidem com assets do arquivo Flask | Comparada para rastrear apresentação; código e dependências não integrados |
| `Logo horizontal FluxoPag com subtítulo.png` | Logo original acessível entre os arquivos do projeto | Copiado para `docs/images/fluxopag-logo.png`, sem redesenhar a identidade |
| Arquivo Figma `Rau8PgbGwiiJwRo9MHgzMW`, frame `12:2` | Dashboard real e estrutura/relações de telas | Prévia exportada para `docs/images/figma-dashboard.png`; explicitamente rotulada como design |

O nome do ZIP não foi usado como prova de completude. Foram inspecionados arquivos, imports, dependências, queries, rotas e assets antes da integração. A coleção representa as fontes **acessíveis nesta revisão**; não afirma reunir toda versão privada ou não disponibilizada de conversas anteriores. A busca de anexos relacionados no Gmail não encontrou fonte adicional; nenhuma mensagem foi enviada.

## Identificação dos arquivos recuperados

| Arquivo | Tamanho | SHA-256 |
| --- | --- | --- |
| `FluxoPag-Flask-MySQL.zip` | 69.359 bytes | `f7f2513c461bd3e881a0fbd07c46d6af7cebf2013b2101c558451f90c659b40d` |
| `FluxoPag_Prototipo_Final.zip` | 9.917 bytes | `462951c98ba914ef09ffc90816fda217e1bf5bbc5f25a8a71c0748e14acf3603` |

Datas de armazenamento de anexos não foram tratadas como data de implementação. Os ZIPs não são a única forma de consultar o projeto: os fontes extraídos estão navegáveis no GitHub.

## Ajustes necessários à consolidação

- Leitura real do `.env` com `python-dotenv`, segredo de sessão local, debug desativado e erro de banco sem detalhes no HTML.
- Inicializador que só aceita banco vazio e seed de produtos fictícios separado.
- Preservação de `order_item_id` e nomes SQL da base; adaptação do código recuperado e conservação do schema anterior em `database/legacy/`.
- Views de histórico usam snapshots; índices úteis da base foram mantidos no schema ampliado.
- Validação de valores monetários finitos, limites das colunas, quatro dígitos ASCII, quantidade acumulada, atualização sem mudança e filtros de datas.
- Correção do intervalo do mês anterior e das agregações/formatos de resumos no MySQL estrito.
- Testes de integração real, CI, documentação e organização do backlog. Funcionalidades grandes ausentes não foram inventadas.

## Referências de apresentação

Foram examinados dois repositórios com atividade recente para adaptar a hierarquia de informações:

- [Pallets / Flask](https://github.com/pallets/flask): entrada curta, explicação de uso e links diretos para documentação e contribuição. Atividade consultada até 08/09/2026.
- [DB Browser for SQLite](https://github.com/sqlitebrowser/sqlitebrowser): screenshot autêntico, descrição prática e instalação organizada. Atividade consultada até 16/09/2026. A referência é de apresentação, não de adoção de SQLite.

O texto foi escrito para o FluxoPag. Não foram copiados código, imagens ou marca desses projetos. A documentação evita badges de release, cobertura ou licença não demonstrados.

## Créditos e licença

A identidade e os assets foram recuperados do próprio contexto FluxoPag; isso registra sua origem, sem inventar uma licença ou um contrato de autoria de terceiros. Não foi encontrado `LICENSE` no repositório auditado. O proprietário deve decidir os termos de uso e confirmar eventuais direitos de terceiros antes de licenciar uma distribuição. Nenhuma licença foi atribuída nesta entrega.
