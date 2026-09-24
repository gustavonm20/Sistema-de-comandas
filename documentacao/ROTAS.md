# Rotas e formulários

[Índice](README.md) · [Arquitetura](ARQUITETURA.md)

Fonte: [aplicacao.py](../aplicacao.py). São 20 regras da aplicação e uma regra de arquivos estáticos; GET também aceita HEAD/OPTIONS conforme o Flask. As respostas são HTML ou redirecionamentos. Não há contrato JSON de API REST separado.

| Método | Caminho | Entrada e responsabilidade |
| --- | --- | --- |
| GET | `/` | Painel com dados de vendas do dia e pedidos abertos. |
| GET | `/produtos` | Filtros `busca`, `id_categoria`, `situacao=todos/ativo/inativo`. |
| GET, POST | `/produtos/novo` | Formulário e cadastro: `nome`, `preco`, `id_categoria`. |
| GET, POST | `/produtos/<int:id_produto>/editar` | Edição dos mesmos campos. |
| POST | `/produtos/<int:id_produto>/situacao` | `ativo=true` ativa; outros valores desativam. |
| GET, POST | `/cartoes` | Lista por `situacao`; POST cadastra `numero_cartao`. |
| POST | `/cartoes/<int:id_cartao>/situacao` | Altera `ativo`; cartão ocupado não pode ser desativado pelo serviço. |
| GET | `/pedidos` | Lista abertos; `tipo_atendimento=todos/mesa/balcao/retirada`. |
| GET, POST | `/pedidos/novo` | `id_cartao`, `tipo_atendimento`, `identificacao_atendimento`, `observacao`; exige operação aberta. |
| GET | `/pedidos/<int:id_pedido>` | Detalhes e busca `busca_produto` no catálogo ativo. |
| POST | `/pedidos/<int:id_pedido>/itens` | Inclui `id_produto`, `quantidade` (padrão 1). |
| POST | `/pedidos/<int:id_pedido>/itens/<int:id_item>/quantidade` | Atualiza `quantidade`. |
| POST | `/pedidos/<int:id_pedido>/itens/<int:id_item>/remover` | Remove item do pedido aberto. |
| GET, POST | `/pedidos/<int:id_pedido>/pagamento` | `forma_pagamento=dinheiro/pix/debito/credito`, `valor_recebido` para dinheiro. |
| GET | `/historico` | `busca`, `forma_pagamento`, `data_inicial`, `data_final`; datas `AAAA-MM-DD`. |
| GET | `/vendas/<int:id_venda>` | Venda e itens históricos. |
| GET | `/resumos` | `periodo=diario/semanal/mensal`; valor desconhecido usa `diario`. |
| GET, POST | `/conta` | Dados `nome`, `correio`, `tipo_estabelecimento` do estabelecimento. |
| POST | `/operacao/abrir` | `caixa_inicial`, saldo inicial não negativo. |
| POST | `/operacao/fechar` | `caixa_contado`, `justificativa_diferenca`; exige ausência de pedidos abertos. |
| GET | `/estaticos/<path:filename>` | CSS, JS e imagens servidos pelo Flask no desenvolvimento. |

`aplicacao.url_map` confirmou 21 regras, contando arquivos estáticos. A tabela inclui todas elas.

## Validação e erros

`servicos.py` valida o domínio, sem confiar apenas em `required`, `min` ou JavaScript do navegador. Produto: nome normalizado de até 100 caracteres, categoria existente/ativa e preço positivo. Cartão: quatro dígitos ASCII. Pedido: mesa exige identificação; identificação até 100 e observação até 255 caracteres. Quantidades: inteiros de 1 a 99 por linha, incluindo a soma de inclusões. Histórico: datas válidas e intervalo em ordem. Estabelecimento: campos obrigatórios e limites das colunas; validação de e-mail é básica, não confirma existência do endereço.

POSTs normalmente capturam `ErroServico`, exibem mensagem e redirecionam (302) ou reapresentam o formulário (200). Erros de serviço não capturados recebem HTML 400; erros do conector recebem HTML 503 genérico e detalhes no registro local. Identificadores inexistentes podem resultar em 400, não há contrato uniforme de 404 de domínio. Erros de programação continuam sendo erros de servidor.

Não há sessão autenticada nem token CSRF; esconder um botão não autoriza nem protege uma operação. Antes de disponibilizar acesso externo, concluir a [#24](https://github.com/gustavonm20/Sistema-de-comandas/issues/24). Para testar POSTs, use dados fictícios em banco isolado e verifique tanto o resultado HTTP quanto os registros gravados.
