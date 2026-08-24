# Roadmap do FluxoPag

Este roadmap separa o trabalho de **design**, **fundação técnica**, **MVP**, **operação**, **indicadores** e **qualidade**. As issues são a fonte de acompanhamento detalhado.

## Marco atual

O projeto entrou na fundação técnica do banco de dados. A primeira versão do schema MySQL já cobre categorias, produtos, comandas físicas, pedidos, itens, vendas e views para histórico e resumos, mantendo alinhamento com os fluxos definidos no Figma.

## Legenda

- ✅ Concluído
- 🚧 Em andamento
- ⏳ Planejado

## Fase 0 — Planejamento e prototipação

Status: 🚧 Em andamento

- 🚧 #1 — Definir funcionalidades e regras de negócio
- 🚧 #2 — Completar protótipo hi-fi e low-fi no Figma
- ⏳ #5 — Criar fluxo de abertura de caixa
- ⏳ #6 — Bloquear fechamento do dia com comandas abertas
- ⏳ #7 — Criar confirmação e fechamento de caixa
- ⏳ #8 — Adicionar comparativos aos resumos
- ⏳ #9 — Completar low-fi e organizar as telas

## Fase 1 — Fundação técnica

Status: 🚧 Em andamento

- ⏳ #3 — Estruturar o projeto e configurar o ambiente
- 🚧 #10 — Modelar banco de dados MySQL e entidades do domínio
- ⏳ #16 — Implementar layout base e navegação
- ⏳ #19 — Implementar migrations versionadas do MySQL

### Já entregue na modelagem

- ✅ MySQL 8 definido como banco relacional do projeto.
- ✅ `categories` e `products`.
- ✅ `command_cards` com número fixo de quatro dígitos.
- ✅ `orders` com proteção contra duas comandas abertas para o mesmo número.
- ✅ `order_items` com quantidade, preço histórico e observações.
- ✅ `sales` com forma de pagamento e data da venda.
- ✅ constraints de integridade.
- ✅ índices iniciais.
- ✅ views para produtos, comandas abertas, detalhes, histórico e resumos.
- ✅ documentação inicial do banco.

### Ainda falta na fundação

- estrutura de estabelecimento/autenticação;
- operação diária e caixa;
- migrations;
- transação atômica de fechamento da comanda;
- integração Python ↔ MySQL.

## Fase 2 — MVP operacional

Status: ⏳ Planejado

- ⏳ #11 — Catálogo e gerenciamento de produtos
- ⏳ #12 — Fluxo completo de comandas
- ⏳ #13 — Pagamentos e histórico de vendas
- ⏳ #21 — Tornar fechamento da comanda transacional

### Resultado esperado

O estabelecimento consegue cadastrar produtos, abrir uma comanda, adicionar itens, receber o pagamento, fechar a comanda e consultar a venda sem risco de persistência parcial.

## Fase 3 — Operação diária, caixa e estoque

Status: ⏳ Planejado

- ⏳ #14 — Abertura, operação e fechamento do caixa
- ⏳ #20 — Controle de estoque e movimentações

### Resultado esperado

O estabelecimento abre o dia com um valor inicial, opera somente durante uma sessão ativa, encerra o caixa com conferência e mantém movimentações de estoque rastreáveis.

## Fase 4 — Indicadores e gestão

Status: 🚧 Base de dados preparada

- ⏳ #15 — Resumos diário, semanal e mensal

As views `vw_daily_summary`, `vw_weekly_summary` e `vw_monthly_summary` já fornecem a base de faturamento, quantidade de vendas e ticket médio. Comparações de período, produtos mais vendidos e gráficos ainda serão implementados.

## Fase 5 — Qualidade e entrega

Status: ⏳ Planejado

- ⏳ #17 — Testes, lint e integração contínua
- ⏳ documentar API e arquitetura;
- ⏳ adicionar Docker;
- ⏳ configurar ambiente de produção;
- ⏳ criar primeira release estável.

## Ordem recomendada de execução

1. Continuar a modelagem da issue #10 até operação diária e caixa.
2. Estruturar o projeto da issue #3 e integrar Python ao MySQL.
3. Preparar migrations na #19 antes de mudanças estruturais mais profundas.
4. Implementar produtos e comandas: #11 e #12.
5. Implementar fechamento financeiro e histórico: #13 + #21.
6. Implementar operação diária: #14.
7. Evoluir estoque: #20.
8. Consumir as views e concluir os indicadores: #15.
9. Finalizar os fluxos pendentes do Figma em paralelo: #5 a #9.
10. Evoluir testes e automação continuamente: #17.

## Fora do primeiro MVP

- múltiplos funcionários e permissões avançadas;
- cancelamentos e estornos completos;
- reabertura controlada de um dia encerrado;
- exportação de relatórios em PDF e Excel;
- tema escuro;
- backup automatizado;
- auditoria avançada;
- integração fiscal.
