# Design e protótipo Figma

[Índice](README.md) · [Estado da implementação](STATUS.md)

Inspeção do arquivo realizada em **17/09/2026**. Essa é a data da revisão, não uma data atribuída à criação das telas.

- [Arquivo de design — FluxoPag / Comandas](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=0-1)
- [Protótipo interativo — entrada no dashboard](https://www.figma.com/proto/Rau8PgbGwiiJwRo9MHgzMW/Comandas?page-id=0%3A1&node-id=12-2&starting-point-node-id=12%3A2)

O segundo endereço usa o frame `12:2`, confirmado como ponto inicial em `flowStartingPoints`. O arquivo e suas reações foram inspecionados; o player completo não foi exercitado de ponta a ponta. Portanto, o endereço do protótipo está separado da referência de edição sem afirmar que toda navegação está concluída.

## Por que prototipar

O protótipo de terminal ajudou a praticar lógica. O Figma tornou o produto pretendido visível: organizar a navegação, explorar a sequência de tarefas do atendente, definir a marca FluxoPag, perceber estados ausentes e orientar a implementação web. Esses são objetivos da fase de prototipação. Não foram encontrados registros que comprovem pesquisa com usuários, testes de usabilidade, validação comercial ou redução de erros no atendimento.

**Low-fi**, ou wireframe, é o rascunho da estrutura: onde ficam as informações e quais ações existem. **Hi-fi** detalha cores, tipografia, ícones, espaçamento e estados mais próximos da interface desejada. Um frame hi-fi, por si só, não comprova que sua ação está conectada nem implementada em Flask.

![Dashboard exportado do Figma, com a identidade azul e laranja do FluxoPag](images/figma-dashboard.png)

*Prévia autêntica de design. Dados ilustrativos, sem vínculo com uma operação real ou com o banco de testes.*

## Telas, finalidade e entrega

Foram encontrados **16 frames hi-fi e 10 low-fi** na página `0:1`. A tabela agrupa apenas estados relacionados para manter a leitura curta. Os links levam aos frames de design; a situação do código refere-se à branch de consolidação.

| Tela / frame hi-fi | Finalidade | Estado do design | Estado da implementação | Issue |
| --- | --- | --- | --- | --- |
| [Dashboard — 12:2](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=12-2) | Visão do atendimento e das vendas | Hi-fi e low-fi `36:444`; textos ilustrativos a revisar | Página Flask e consultas testadas; gráfico limita horas a 08h–20h | #16, #15 |
| [Produtos — 12:3](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=12-3) | Consultar e administrar catálogo | Hi-fi e low-fi `36:463` | CRUD MySQL verificado; revisão visual pendente | #11 |
| [Comandas — 12:4](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=12-4) | Localizar atendimentos abertos | Hi-fi e low-fi `36:485` | Listagem e filtros presentes | #12 |
| [Nova comanda — 36:2](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=36-2) | Escolher número e atendimento | Hi-fi e low-fi `36:570`; abrir/cancelar têm reações | Criação vinculada à operação; concorrência pendente | #12, #14 |
| [Detalhes — 12:5](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=12-5) | Incluir itens e acompanhar total | Hi-fi e low-fi `36:510`; ligação para pagamento | Itens e totais testados em sequência; corrida com fechamento pendente | #12, #21 |
| [Pagamento — 12:6](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=12-6) | Informar meio e confirmar registro | Hi-fi e low-fi `36:527`; ligação para histórico | Registro, troco e rollback testados; sem provedor financeiro | #13 |
| [Histórico — 12:7](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=12-7) | Consultar vendas anteriores | Hi-fi e low-fi `36:547` | Filtros e detalhes presentes; navegação GET testada | #13 |
| [Conta, dia fechado — 36:269](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=36-269) | Dados do estabelecimento e iniciar operação | Hi-fi e low-fi `36:601`; iniciar pula abertura de caixa | Dados editáveis e formulário de abertura; sem login | #5, #14, #24 |
| [Conta, dia aberto — 41:2](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=41-2) | Acompanhar operação e encerrar | Hi-fi e low-fi `42:6`; finalizar pula estados intermediários | Caixa persistido e bloqueio sequencial testados | #6, #7, #14 |
| [Abertura de caixa — 71:2](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=71-2) | Informar saldo inicial | Hi-fi presente; low-fi específico e ações do modal não localizados | Formulário na conta; não replica esse modal | #5 |
| [Fechamento bloqueado — 71:120](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=71-120) | Explicar pendências | Hi-fi presente; low-fi e ações do modal ausentes na inspeção | Serviço bloqueia; interface usa mensagem, sem equivalência completa | #6 |
| [Confirmação — 72:2](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=72-2) | Rever impacto do encerramento | Hi-fi presente; low-fi e ações do modal pendentes | Confirmação simples em JavaScript; falta revisar equivalência | #7 |
| [Conferência — 72:147](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=72-147) | Contado, esperado e diferença | Hi-fi presente; low-fi e ações do modal pendentes | Campos na conta e cálculo no backend; fluxo parcial | #7, #14 |
| [Dia — 41:102](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=41-102) | Resumo diário | Hi-fi; low-fi genérico de resumos `42:33` | `/reports?period=daily`; não seleciona operação encerrada | #8, #15 |
| [Semana — 41:227](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=41-227) | Resumo semanal | Hi-fi; aba conectada; comparativos pendentes | `/reports?period=weekly`; semana começa segunda | #8, #15 |
| [Mês — 41:352](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=41-352) | Resumo mensal | Hi-fi; aba conectada; comparativos pendentes | `/reports?period=monthly`; mês de calendário | #8, #15 |

## Navegação inspecionada

Detalhes encaminha ao pagamento (`12:5 → 12:6`); confirmar pagamento encaminha ao histórico (`12:6 → 12:7`). Nova comanda abre detalhes ou volta à listagem. As abas dia/semana/mês têm ligações entre si. Há atalhos de nova comanda e perfil nos frames principais.

Na conta com dia fechado, **Iniciar dia** leva diretamente de `36:269` a `41:2`, sem passar por `71:2`. Na conta aberta, **Finalizar dia** leva diretamente ao resumo `41:102`, sem atravessar bloqueio, confirmação e conferência. Nos quatro novos frames de caixa, os botões dos modais não apresentaram reações; ligações herdadas do fundo não completam o fluxo. Não foi comprovada a navegação de todos os itens laterais.

## Diferenças e próximos ajustes de design

- Os frames novos de caixa existem; as issues #5–#7 continuam abertas por low-fi e conexões incompletas.
- #8 ainda precisa de comparativos e estados sem dados: não foram localizados rótulos de comparação ao período anterior nas três telas hi-fi de resumo.
- #9 concentra nomes/numeração repetida de frames, sequência, espaçamento e revisão das conexões. Há vários inícios com nomes genéricos como `Flow 2`.
- O dashboard ainda tem exemplos com três dígitos e texto temporal como “+3 desde às 10h”. A regra do produto exige quatro dígitos; esses exemplos não alteram o requisito.
- A web recuperada tem tema escuro, página de cartões e detalhes de venda; isso não comprova frames equivalentes no Figma.
- A tela de conta no Figma contém intenções de sessão; a web não implementa autenticação. A #24 acompanha essa lacuna.

A organização do repositório não alterou o arquivo Figma. Concluir o design significa revisar os caminhos e estados, sem marcar os recursos da aplicação como prontos apenas por existirem telas.
