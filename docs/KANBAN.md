# Organização sugerida do Kanban

O quadro deve usar um fluxo simples para não duplicar informação já existente nas issues.

## Colunas

### Backlog

Tarefas definidas, mas que ainda não devem ser iniciadas.

- #3 — Estruturar o projeto e configurar o ambiente
- #10 — Modelar banco de dados e entidades
- #11 — Produtos
- #12 — Comandas
- #13 — Pagamentos e histórico
- #14 — Operação e caixa
- #15 — Resumos
- #16 — Layout base e navegação
- #17 — Testes e integração contínua

### Todo

Tarefas prontas para começar, sem bloqueios de definição.

- #5 — Abertura de caixa no Figma
- #6 — Bloqueio com comandas abertas
- #7 — Confirmação e fechamento de caixa
- #8 — Comparativos dos resumos

### In Progress

Tarefas em execução ativa. Recomenda-se manter no máximo duas tarefas nesta coluna.

- #1 — Funcionalidades e regras de negócio
- #2 — Protótipo hi-fi e low-fi

### Review

Tarefas concluídas que precisam de revisão visual, funcional ou de código.

- mover para cá quando uma issue possuir entrega pronta;
- revisar critérios de aceitação;
- validar o fluxo no Figma ou os testes no pull request.

### Done

Tarefas concluídas, revisadas e integradas.

- #4 — Issue duplicada do protótipo

## Política de movimentação

1. Uma tarefa sai do Backlog quando suas dependências estiverem resolvidas.
2. Antes de mover para In Progress, confirme os critérios de aceitação.
3. Evite mais de duas tarefas simultâneas em In Progress.
4. Use Review para validar antes de encerrar a issue.
5. Só mova para Done depois de atualizar documentação e fechar a issue.

## Ordem imediata recomendada

1. Concluir #5, #6, #7 e #8.
2. Executar #9 para organizar o arquivo do Figma.
3. Revisar e encerrar #2.
4. Finalizar as pendências restantes da #1.
5. Iniciar #3 e #10.
