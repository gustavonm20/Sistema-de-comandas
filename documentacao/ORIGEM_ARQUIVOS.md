# Origem dos arquivos e decisões de integração

[Índice](README.md) · [Mudanças](../ALTERACOES.md)

Revisão em 17/09/2026. A referência inicial do GitHub foi `main` em `9c0317fe190917e12f1966d1b454f266986e8a1d`. Foram comparados os arquivos dessa base, ramos relevantes, solicitações de integração #18, #22 e #23 já integradas, tarefas abertas/fechadas e os artefatos acessíveis. Esta consolidação não reescreveu registros anteriores. A tradução de 19/09/2026 também acrescenta apenas novos registros.

## Fontes examinadas

| Fonte | Conteúdo observado | Destino / decisão |
| --- | --- | --- |
| Repositório na base auditada | Protótipo Python, estrutura SQL e documentos; sem aplicação Flask completa | Histórico preservado; documentos reconciliados com o código |
| `FluxoPag-Flask-MySQL.zip` | Quatro módulos Python, 15 modelos, CSS, JS, imagens, estrutura, dependências e testes iniciais | Fonte web extraída na raiz, revisada e corrigida |
| `FluxoPag_Prototipo_Final.zip` | Evolução de terminal com serviços, persistência JSON e seis testes | Preservado em `legado/terminal-json/`, sem alimentar a web |
| Fonte anterior do protótipo de interface, registro de alteração `ff28c1604811233331926f2884e99b8f75b456f3` | React/Next/vinext, Tailwind e Drizzle, fora do conjunto de tecnologias acordado; marca e ícones coincidem com recursos do arquivo Flask | Comparada para rastrear apresentação; código e dependências não integrados |
| `Logo horizontal FluxoPag com subtítulo.png` | Logo original acessível entre os arquivos do projeto | Copiado para `documentacao/imagens/fluxopag-logotipo.png`, sem redesenhar a identidade |
| Arquivo Figma `Rau8PgbGwiiJwRo9MHgzMW`, quadro `12:2` | Painel real e estrutura/relações de telas | Prévia exportada para `documentacao/imagens/figma-painel.png`; explicitamente rotulada como projeto visual |

O nome do ZIP não foi usado como prova de completude. Foram inspecionados arquivos, importações, dependências, consultas, rotas e recursos antes da integração. A coleção representa as fontes **acessíveis nesta revisão**; não afirma reunir toda versão privada ou não disponibilizada de conversas anteriores. A busca de anexos relacionados no Gmail não encontrou fonte adicional; nenhuma mensagem foi enviada.

## Identificação dos arquivos recuperados

| Arquivo | Tamanho | SHA-256 |
| --- | --- | --- |
| `FluxoPag-Flask-MySQL.zip` | 69.359 bytes | `f7f2513c461bd3e881a0fbd07c46d6af7cebf2013b2101c558451f90c659b40d` |
| `FluxoPag_Prototipo_Final.zip` | 9.917 bytes | `462951c98ba914ef09ffc90816fda217e1bf5bbc5f25a8a71c0748e14acf3603` |

Datas de armazenamento de anexos não foram tratadas como data de implementação. Os ZIPs não são a única forma de consultar o projeto: os fontes extraídos estão navegáveis no GitHub.

## Ajustes necessários à consolidação

- Leitura real do `.env` com `python-dotenv`, segredo de sessão local, depuração desativada e erro de banco sem detalhes no HTML.
- Inicializador que só aceita banco vazio e dados iniciais de produtos fictícios separado.
- Preservação de `id_item_pedido` e nomes SQL da base; adaptação do código recuperado e conservação da estrutura anterior em `banco_dados/legado/`.
- Visões de histórico usam cópias históricas; índices úteis da base foram mantidos na estrutura ampliada.
- Validação de valores monetários finitos, limites das colunas, quatro dígitos ASCII, quantidade acumulada, atualização sem mudança e filtros de datas.
- Correção do intervalo do mês anterior e das agregações/formatos de resumos no MySQL estrito.
- Testes de integração real, integração contínua, documentação e organização da lista de pendências. Funcionalidades grandes ausentes não foram inventadas.

## Referências de apresentação

Foram examinados dois repositórios com atividade recente para adaptar a hierarquia de informações:

- [Pallets / Flask](https://github.com/pallets/flask): entrada curta, explicação de uso e ligações diretas para documentação e contribuição. Atividade consultada até 08/09/2026.
- [DB Browser for SQLite](https://github.com/sqlitebrowser/sqlitebrowser): captura de tela autêntica, descrição prática e instalação organizada. Atividade consultada até 16/09/2026. A referência é de apresentação, não de adoção de SQLite.

O texto foi escrito para o FluxoPag. Não foram copiados código, imagens ou marca desses projetos. A documentação evita selos de versão, cobertura ou licença não demonstrados.

## Créditos e licença

A identidade e os recursos foram recuperados do próprio contexto FluxoPag; isso registra sua origem, sem inventar uma licença ou um contrato de autoria de terceiros. Não foi encontrado `LICENSE` no repositório auditado. O proprietário deve decidir os termos de uso e confirmar eventuais direitos de terceiros antes de licenciar uma distribuição. Nenhuma licença foi atribuída nesta entrega.

## Tradução de 19/09/2026

As fontes recuperadas receberam nomes próprios em português, incluindo os dois protótipos. A estrutura e as regras continuam usando MySQL. As imagens originais, os endereços externos e as referências históricas foram mantidos para preservar sua autenticidade. Os nomes anteriores necessários para ler dados persistidos ficam na compatibilidade e nos testes correspondentes. O histórico Git anterior à tradução continua acessível.
