# Visão do produto

[Índice](README.md) · [Estado real](SITUACAO.md)

O FluxoPag — Sistema de Comandas é uma aplicação prática em evolução para padarias, restaurantes, cafés e pequenos estabelecimentos. Seu público principal é a equipe que registra o consumo e recebe o pagamento, além de quem acompanha a operação.

## Problema e objetivos

Um atendimento precisa continuar compreensível desde o primeiro item até o fechamento: identificar a comanda correta, consultar o consumo, calcular o total, registrar a forma de pagamento e consultar a venda depois de liberar o número. Na operação diária, é necessário separar dinheiro em caixa de vendas por outros meios e conferir diferenças.

Os objetivos são centralizar esse registro, tornar os estados visíveis e preservar informações suficientes para histórico e resumos. São objetivos de produto, sem alegação de validação com clientes ou redução medida de erros.

## Evolução

O protótipo inicial de terminal foi criado para praticar e visualizar a lógica de Python. A evolução em JSON amplia esse treino, mas continua isolada do produto web. O Figma transformou requisitos em telas e estados. A modelagem MySQL acrescentou persistência e integridade. A versão Flask recuperada aproxima essa experiência visual do servidor; a consolidação está integrada à `main`, com execução aprovada no MySQL e lacunas de produto e integração ainda abertas.

## Escopo

O núcleo inclui catálogo, comandas reutilizáveis, itens, registro de pagamentos, histórico, conta do estabelecimento, operação diária, conferência de caixa e visões distintas de dia, semana e mês. No código recuperado, cada instalação representa um estabelecimento; não há isolamento entre vários clientes nem autenticação.

Estoque possui uma tarefa própria e permanece extensão posterior. Integração bancária, emissão fiscal, estornos, permissões de funcionários, reabertura controlada, cópia de segurança automatizado e exportações não são entregas demonstradas do MVP atual.

## Fluxo pretendido e diferenças

O estabelecimento prepara os produtos, abre o caixa, atende pelas comandas, registra os pagamentos e encerra o dia após resolver as pendências. A implementação já contém funções para essas etapas, mas o comportamento simultâneo precisa de verificação e os resumos usam calendário em vez de uma sessão encerrada.

Consulte [regras](REGRAS_NEGOCIO.md), [Figma](FIGMA.md) e [planejamento](../PLANEJAMENTO.md) para as decisões e lacunas, sem tratar uma tela desenhada como funcionalidade pronta.
