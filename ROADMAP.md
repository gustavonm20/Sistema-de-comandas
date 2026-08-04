# Roadmap do FluxoPag

Este roadmap separa o trabalho de **design**, **fundação técnica**, **MVP** e **qualidade**. As issues são a fonte de acompanhamento detalhado.

## Marco atual

O projeto está na fase de planejamento e prototipação. A próxima entrega recomendada é a [issue #5 — Criar fluxo de abertura de caixa](https://github.com/gustavonm20/Sistema-de-comandas/issues/5), seguida pelas issues de bloqueio e fechamento do dia.

## Legenda

- ✅ Concluído
- 🚧 Em andamento
- ⏳ Planejado

## Fase 0 — Planejamento e prototipação

Status: 🚧 Em andamento

- 🚧 [#1 — Definir funcionalidades e regras de negócio](https://github.com/gustavonm20/Sistema-de-comandas/issues/1)
- 🚧 [#2 — Completar protótipo hi-fi e low-fi no Figma](https://github.com/gustavonm20/Sistema-de-comandas/issues/2)
- ⏳ [#5 — Criar fluxo de abertura de caixa](https://github.com/gustavonm20/Sistema-de-comandas/issues/5)
- ⏳ [#6 — Bloquear fechamento do dia com comandas abertas](https://github.com/gustavonm20/Sistema-de-comandas/issues/6)
- ⏳ [#7 — Criar confirmação e fechamento de caixa](https://github.com/gustavonm20/Sistema-de-comandas/issues/7)
- ⏳ [#8 — Adicionar comparativos aos resumos](https://github.com/gustavonm20/Sistema-de-comandas/issues/8)
- ⏳ [#9 — Completar low-fi e organizar as telas](https://github.com/gustavonm20/Sistema-de-comandas/issues/9)

### Resultado esperado

Protótipo navegável, organizado e consistente, com hi-fi e low-fi dos fluxos essenciais.

## Fase 1 — Fundação da aplicação

Status: ⏳ Planejado

- ⏳ [#3 — Estruturar o projeto e configurar o ambiente](https://github.com/gustavonm20/Sistema-de-comandas/issues/3)
- ⏳ [#10 — Modelar banco de dados e entidades](https://github.com/gustavonm20/Sistema-de-comandas/issues/10)
- ⏳ [#16 — Implementar layout base e navegação](https://github.com/gustavonm20/Sistema-de-comandas/issues/16)

### Resultado esperado

Aplicação Flask executando localmente, estrutura de pastas definida, banco SQLite configurado e layout compartilhado pronto.

## Fase 2 — MVP operacional

Status: ⏳ Planejado

- ⏳ [#11 — Catálogo e gerenciamento de produtos](https://github.com/gustavonm20/Sistema-de-comandas/issues/11)
- ⏳ [#12 — Fluxo completo de comandas](https://github.com/gustavonm20/Sistema-de-comandas/issues/12)
- ⏳ [#13 — Pagamentos e histórico de vendas](https://github.com/gustavonm20/Sistema-de-comandas/issues/13)

### Resultado esperado

O estabelecimento consegue cadastrar produtos, abrir uma comanda, adicionar itens, receber o pagamento, fechar a comanda e consultar a venda.

## Fase 3 — Operação diária e caixa

Status: ⏳ Planejado

- ⏳ [#14 — Abertura, operação e fechamento do caixa](https://github.com/gustavonm20/Sistema-de-comandas/issues/14)

### Resultado esperado

O estabelecimento abre o dia com um valor inicial, opera somente durante uma sessão ativa e encerra o caixa com conferência e registro de divergências.

## Fase 4 — Indicadores e gestão

Status: ⏳ Planejado

- ⏳ [#15 — Resumos diário, semanal e mensal](https://github.com/gustavonm20/Sistema-de-comandas/issues/15)

### Resultado esperado

Dashboard e resumos calculados a partir das vendas reais, incluindo comparação com períodos anteriores.

## Fase 5 — Qualidade e entrega

Status: ⏳ Planejado

- ⏳ [#17 — Testes, lint e integração contínua](https://github.com/gustavonm20/Sistema-de-comandas/issues/17)
- ⏳ Documentar API e arquitetura.
- ⏳ Adicionar Docker.
- ⏳ Configurar ambiente de produção.
- ⏳ Criar uma primeira release estável.

## Ordem recomendada de execução

1. Finalizar o Figma: #2, #5, #6, #7, #8 e #9.
2. Preparar a base técnica: #3, #10 e #16.
3. Construir o núcleo do MVP: #11, #12 e #13.
4. Implementar operação e caixa: #14.
5. Implementar indicadores: #15.
6. Evoluir testes e automação continuamente: #17.

## Fora do primeiro MVP

- múltiplos funcionários e permissões;
- cancelamentos e estornos;
- reabertura controlada de um dia encerrado;
- exportação de relatórios em PDF e Excel;
- tema escuro;
- notificações e alertas de estoque;
- backup automatizado;
- auditoria avançada;
- integração fiscal.
