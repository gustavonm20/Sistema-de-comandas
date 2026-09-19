# Rotas e formulários

[Índice](README.md) · [Arquitetura](ARCHITECTURE.md)

Fonte: [app.py](../app.py). São 20 regras da aplicação e uma regra de arquivos estáticos; GET também aceita HEAD/OPTIONS conforme o Flask. As respostas são HTML ou redirecionamentos. Não há contrato JSON de API REST separado.

| Método | Caminho | Entrada e responsabilidade |
| --- | --- | --- |
| GET | `/` | Dashboard com dados de vendas do dia e pedidos abertos. |
| GET | `/products` | Filtros `search`, `category_id`, `status=all/active/inactive`. |
| GET, POST | `/products/new` | Formulário e cadastro: `name`, `price`, `category_id`. |
| GET, POST | `/products/<int:product_id>/edit` | Edição dos mesmos campos. |
| POST | `/products/<int:product_id>/status` | `active=true` ativa; outros valores desativam. |
| GET, POST | `/cards` | Lista por `status`; POST cadastra `card_number`. |
| POST | `/cards/<int:card_id>/status` | Altera `active`; cartão ocupado não pode ser desativado pelo serviço. |
| GET | `/orders` | Lista abertos; `service_type=all/table/counter/pickup`. |
| GET, POST | `/orders/new` | `card_id`, `service_type`, `service_label`, `note`; exige operação aberta. |
| GET | `/orders/<int:order_id>` | Detalhes e busca `product_search` no catálogo ativo. |
| POST | `/orders/<int:order_id>/items` | Inclui `product_id`, `quantity` (padrão 1). |
| POST | `/orders/<int:order_id>/items/<int:item_id>/quantity` | Atualiza `quantity`. |
| POST | `/orders/<int:order_id>/items/<int:item_id>/remove` | Remove item do pedido aberto. |
| GET, POST | `/orders/<int:order_id>/payment` | `payment_method=cash/pix/debit/credit`, `cash_received` para dinheiro. |
| GET | `/history` | `search`, `payment_method`, `date_from`, `date_to`; datas `AAAA-MM-DD`. |
| GET | `/sales/<int:sale_id>` | Venda e itens históricos. |
| GET | `/reports` | `period=daily/weekly/monthly`; valor desconhecido usa `daily`. |
| GET, POST | `/account` | Dados `name`, `email`, `business_type` do estabelecimento. |
| POST | `/operation/open` | `opening_cash`, saldo inicial não negativo. |
| POST | `/operation/close` | `counted_cash`, `discrepancy_note`; exige ausência de pedidos abertos. |
| GET | `/static/<path:filename>` | CSS, JS e imagens servidos pelo Flask no desenvolvimento. |

`app.url_map` confirmou 21 regras, contando arquivos estáticos. A tabela inclui todas elas.

## Validação e erros

`services.py` valida o domínio, sem confiar apenas em `required`, `min` ou JavaScript do navegador. Produto: nome normalizado de até 100 caracteres, categoria existente/ativa e preço positivo. Cartão: quatro dígitos ASCII. Pedido: mesa exige identificação; identificação até 100 e observação até 255 caracteres. Quantidades: inteiros de 1 a 99 por linha, incluindo a soma de inclusões. Histórico: datas válidas e intervalo em ordem. Estabelecimento: campos obrigatórios e limites das colunas; validação de e-mail é básica, não confirma existência do endereço.

POSTs normalmente capturam `ServiceError`, exibem mensagem e redirecionam (302) ou reapresentam o formulário (200). Erros de serviço não capturados recebem HTML 400; erros do conector recebem HTML 503 genérico e detalhes no log local. Identificadores inexistentes podem resultar em 400, não há contrato uniforme de 404 de domínio. Erros de programação continuam sendo erros de servidor.

Não há sessão autenticada nem token CSRF; esconder um botão não autoriza nem protege uma operação. Antes de disponibilizar acesso externo, concluir a [#24](https://github.com/gustavonm20/Sistema-de-comandas/issues/24). Para testar POSTs, use dados fictícios em banco isolado e verifique tanto o resultado HTTP quanto os registros gravados.
