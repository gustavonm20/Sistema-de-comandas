# Organização sugerida do Kanban

O quadro deve refletir o estado real do projeto sem duplicar o detalhamento das issues. Este arquivo registra a organização recomendada; a movimentação visual do GitHub Projects deve acompanhar estas mudanças.

## Backlog

- #11 — Catálogo e gerenciamento de produtos
- #12 — Fluxo completo de comandas
- #13 — Pagamentos e histórico
- #14 — Operação e caixa
- #15 — Resumos
- #16 — Layout base e navegação
- #17 — Testes e integração contínua
- Controle de estoque e movimentações
- Migrations do banco
- Backup e restauração

## Todo

- #3 — Estruturar o projeto e configurar o ambiente
- #5 — Abertura de caixa no Figma
- #6 — Bloqueio com comandas abertas
- #7 — Confirmação e fechamento de caixa
- #8 — Comparativos dos resumos
- #9 — Organizar hi-fi e low-fi

## In Progress

- #1 — Funcionalidades e regras de negócio
- #2 — Protótipo hi-fi e low-fi
- #10 — Modelar banco de dados e entidades

### Progresso atual de #10

- schema MySQL inicial criado;
- categorias e produtos modelados;
- comandas físicas e reutilizáveis modeladas;
- pedidos e itens modelados;
- vendas modeladas;
- proteção contra duas utilizações abertas da mesma comanda;
- views de produtos, comandas abertas, histórico e resumos criadas;
- documentação do banco criada.

## Review

Mover para esta coluna quando uma entrega estiver pronta para validação visual, funcional ou de código.

Critérios mínimos:

- critérios de aceitação revisados;
- documentação atualizada;
- alterações integradas por pull request quando aplicável;
- validação do Figma para mudanças visuais;
- validação de schema/consultas para mudanças de banco.

## Done

- #4 — Issue duplicada do protótipo
- PR #18 — Organização inicial de roadmap, regras e acompanhamento do Figma

## Política de movimentação

1. Uma tarefa sai do Backlog quando suas dependências estiverem resolvidas.
2. Antes de mover para In Progress, confirme os critérios de aceitação.
3. Evite muitas frentes simultâneas; priorize terminar a modelagem do banco e estruturar a aplicação.
4. Use Review para validar antes de encerrar uma issue.
5. Só mova para Done depois de atualizar documentação e fechar a issue.
6. Mudanças relevantes de código ou schema devem passar por branch e pull request.

## Ordem imediata recomendada

1. Consolidar a primeira etapa da issue #10 no MySQL.
2. Modelar operação diária/caixa e estabelecimento.
3. Iniciar #3 com a conexão Python ↔ MySQL.
4. Começar #11 e #12 sobre a estrutura persistente.
5. Continuar em paralelo as pendências do Figma #5 a #9.
