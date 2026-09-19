# FluxoPag — Protótipo de Comandas

Protótipo completo em Python para terminal. Os dados ficam salvos automaticamente em JSON.

## Funcionalidades

- Cadastro, listagem, pesquisa, edição e desativação de produtos.
- 20 comandas fixas, numeradas e reutilizáveis.
- Inclusão e remoção de produtos, visualização e fechamento com confirmação.
- Pagamentos em dinheiro, Pix, crédito ou débito.
- Histórico permanente das vendas.
- Abertura e fechamento do dia, com bloqueio enquanto houver comandas abertas.
- Conferência do dinheiro e cálculo de diferença de caixa.
- Resumos separados por dia, semana e mês, com faturamento, ticket médio, formas de pagamento, produtos mais vendidos e comparação com o período anterior.

## Como executar

1. Instale o Python 3.10 ou superior.
2. Abra o terminal dentro desta pasta.
3. Execute:

```bash
python main.py
```

No Windows, caso `python` não funcione, use `py main.py`.

O arquivo `data/database.json` será criado automaticamente na primeira execução. Não é necessário instalar bibliotecas.
