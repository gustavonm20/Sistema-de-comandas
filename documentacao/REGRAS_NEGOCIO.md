# Regras de negócio e decisões pendentes

[Índice](README.md) · [Evidências](SITUACAO.md) · [Banco](BANCO_DADOS.md)

Os requisitos abaixo preservam a visão do proprietário. A coluna de comportamento descreve o código recuperado e consolidado; testes não significam que todos os cenários operacionais estejam resolvidos.

| Tema | Regra pretendida | Comportamento atual |
| --- | --- | --- |
| Identificação | Número fixo e reutilizável de quatro dígitos, sem nome do cliente obrigatório. | `CHAR(4)` e validação ASCII; identificação de mesa é opcional fora do tipo mesa. |
| Ocupação | Um cartão físico não pode ter dois atendimentos abertos. | Coluna gerada e índice único garantem a exclusividade. |
| Histórico | Fechar libera o número sem apagar o atendimento. | Pedido fica `fechado`; itens e venda permanecem. |
| Produtos | Nome, categoria, preço e estado ativo/inativo. | cadastro, consulta, edição e desativação parcial sem exclusão física; categorias vêm do banco, sem tela de manutenção. |
| Inatividade | Produto inativo permanece no histórico e não entra em novo consumo. | Serviço bloqueia inclusão; cópias históricas preservam dados anteriores. |
| Preço histórico | Reajustar catálogo não altera preço já registrado. | `itens_pedido.preco_unitario` guarda o preço da primeira inclusão daquele produto no pedido. |
| Pagamento | Registrar recebimento e preservar venda. | Dinheiro, Pix, débito e crédito são escolhas registradas localmente. Não há processamento financeiro externo. |
| Operação | Abrir antes de atender; conferir caixa ao encerrar; bloquear encerramento com pedidos abertos. | Serviços e tela presentes; falta completar segurança sob concorrência. |
| Resumos | Visões distintas diária, semanal e mensal. | Três consultas/páginas por período de calendário; alinhamento com operação encerrada pendente. |

## Valores e pagamento

A aplicação exige preço de produto **maior que zero**. O banco mantém `CHECK(preco >= 0)` da base histórica. Essa diferença é preservada até uma decisão sobre produtos gratuitos ([#1](https://github.com/gustavonm20/Sistema-de-comandas/issues/1), [#11](https://github.com/gustavonm20/Sistema-de-comandas/issues/11)); ela não autoriza anunciar suporte a preço zero na interface. Inserções diretas no SQL podem passar por restrições diferentes das regras do serviço.

Valores usam duas casas e `Decimal`; a entrada aceita vírgula decimal. Quantidades são inteiras entre 1 e 99 por produto no pedido. Não há consumo fracionado, desconto, gorjeta, taxa de serviço, parcelamento, pagamento dividido ou estorno implementado.

Um pedido vazio ou com total não positivo não pode ser pago. Em dinheiro, o recebido deve cobrir o total; o troco é recebido menos total. Pix e cartões apenas registram o meio informado pelo atendente, sem confirmar transferência, gerar cobrança ou conversar com banco/adquirente.

O fechamento grava venda, situação e auditoria em uma transação. Uma falha deve preservar o pedido aberto e não deixar venda parcial. Há testes reais desse reversão e de repetição sequencial de fechamento; disputas entre conexões ainda são uma entrega separada na [#21](https://github.com/gustavonm20/Sistema-de-comandas/issues/21).

## Operação e caixa

- Existe um estabelecimento local, editável pela tela de conta. E-mail não é credencial; não há autenticação, senha ou autorização.
- O saldo inicial e o dinheiro contado aceitam zero; devem ser não negativos.
- Saldo esperado = saldo inicial + total das vendas em dinheiro ligadas à operação. Pix, débito e crédito não entram no dinheiro físico.
- Divergência = contado − esperado; valor diferente de zero exige justificativa entre 5 e 255 caracteres.
- O fechamento verifica se há pedidos abertos. Não existe cancelamento de comanda vazia; esse caso precisa de regra e entrega em #12.
- A operação pode atravessar meia-noite. Não há reabertura, sangria ou suprimento posterior. `DATETIME` não carrega fuso; servidor Python e MySQL devem estar alinhados.
- A criação de pedidos ainda não compartilha o bloqueio da operação usado no encerramento. O bloqueio de pedidos pendentes está verificado em sequência, não sob corrida (#14).

## Pontos que precisam de decisão ou implementação

| Questão | Evidência / diferença | Encaminhamento |
| --- | --- | --- |
| Catálogo muda durante o atendimento | Nova inclusão do mesmo produto soma quantidade na linha existente e usa o preço inicial. | Definir se novas unidades terão outro preço; não reescrever unidades antigas (#1, #12). |
| Edição disputa com fechamento | Situação do pedido é lido antes da transação de itens. | Bloqueio comum e testes simultâneos (#21). |
| Cancelamento de pedido vazio | Não é possível pagar total zero nem cancelar pela interface. | Definir cancelamento, motivo e preservação do registro (#12). |
| Resumo de operação encerrada | Resumo atual usa data da venda, sem seleção de operação histórica. | Alinhar filtro e nomenclatura (#15). |
| Comparação de períodos | Período atual incompleto é comparado ao anterior completo; semana começa segunda, mês é calendário. | Definir comparação equivalente e seleção de datas (#8, #15). |
| Gráfico do painel | Barras cobrem 08h–20h, embora indicadores somem todas as vendas do dia. | Ajustar recorte e rótulo conforme decisão (#15, #16). |
| Dados e acesso | Ator de auditoria fixo; formulários sem CSRF. | Autenticação e proteção antes de exposição pública (#24). |
| Estoque | Não existe saldo ou baixa na aplicação recuperada. | Extensão posterior, sem bloquear o catálogo básico (#20). |

As decisões devem ser registradas na tarefa e refletidas em testes, documentos e Figma. Documentação isolada não encerra a implementação.
