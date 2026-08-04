# Regras de Negócio

Este documento registra as regras atualmente definidas para o FluxoPag. Alterações relevantes devem atualizar este arquivo e a issue #1.

## 1. Conta do estabelecimento

- A conta autenticada representa o estabelecimento.
- A primeira versão não depende de um funcionário específico para funcionar.
- Os dados da conta incluem nome do estabelecimento, e-mail, tipo de negócio e preferências do sistema.
- A conta exibe o estado atual da operação: aberta ou fechada.

## 2. Operação diária

- O estabelecimento deve iniciar o dia antes de contabilizar vendas e comandas.
- A abertura registra data, horário e valor inicial do caixa.
- Somente uma operação diária pode permanecer aberta por vez.
- Enquanto a operação estiver aberta, vendas, comandas e faturamento são contabilizados no período.
- O encerramento exige confirmação explícita.
- O dia não pode ser finalizado enquanto existirem comandas abertas.
- Ao concluir o fechamento, os dados do período ficam disponíveis nos resumos.

## 3. Caixa

- A abertura de caixa registra um valor inicial.
- O fechamento calcula o valor esperado em dinheiro.
- O usuário informa o valor efetivamente contado.
- O sistema calcula a diferença entre valor esperado e valor contado.
- Quando houver divergência, uma observação deve ser registrada.
- A conferência fica vinculada à operação diária correspondente.

## 4. Produtos

- Cada produto possui identificador, nome, categoria, preço e estado ativo ou inativo.
- Produtos inativos permanecem no histórico, mas não podem ser adicionados a novas comandas.
- O preço deve ser maior que zero.
- Alterações de produto não devem apagar informações de vendas já concluídas.

## 5. Comandas

- A comanda é identificada por um número fixo e reutilizável.
- Não é obrigatório informar o nome do cliente.
- Uma comanda ocupada não pode ser aberta novamente.
- Uma comanda aberta pode receber, alterar e remover itens.
- O total deve ser recalculado após qualquer alteração.
- Uma comanda fechada não pode mais ser editada.
- Após pagamento e fechamento, o número é liberado para um novo atendimento.

## 6. Pagamentos

- As formas previstas para o MVP são dinheiro, Pix, cartão de débito e cartão de crédito.
- Pagamentos em dinheiro devem calcular o troco.
- A venda somente é registrada depois da confirmação do pagamento.
- O valor pago deve corresponder ao total final da comanda.
- O pagamento registra data, horário, valor e forma utilizada.

## 7. Histórico

- Toda comanda paga gera um registro permanente no histórico.
- O histórico deve preservar itens, quantidades, valores, forma de pagamento e identificação da comanda.
- As vendas podem ser filtradas por período e forma de pagamento.
- Alterações posteriores em produtos não modificam vendas antigas.

## 8. Resumos

- O resumo diário usa os dados da operação encerrada.
- Os resumos semanal e mensal consolidam as vendas dos respectivos períodos.
- Os indicadores iniciais são:
  - comandas atendidas;
  - vendas realizadas;
  - faturamento;
  - ticket médio;
  - desempenho por faixa de horário, dia ou semana;
  - produtos mais vendidos.
- O sistema deve comparar o período selecionado com o período anterior equivalente.
- Períodos sem dados devem possuir um estado vazio claro.

## 9. Regras ainda pendentes

- permissões e perfis de funcionários;
- cancelamento de vendas;
- estorno de pagamentos;
- reabertura controlada de uma operação encerrada;
- retiradas e reforços manuais de caixa;
- política de backup e retenção;
- integração fiscal.
