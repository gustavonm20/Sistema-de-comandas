# Roadmap do FluxoPag

[README](README.md) · [Evidências](docs/STATUS.md) · [Kanban existente](https://github.com/users/gustavonm20/projects/2/views/4)

Revisado em 17/09/2026. As fases organizam dependências; não são versões lançadas, percentuais ou compromissos de prazo. A entrega consolidada está em revisão na branch `chore/consolidar-fluxopag`. Nenhuma issue foi encerrada só pela publicação dos arquivos.

| Fase | Base disponível | Próxima entrega verificável | Issues |
| --- | --- | --- | --- |
| Fundamentos | Python histórico, schema ampliado, Flask e configuração recuperados | Revisar setup, decisões abertas e evolução do banco sem perda | [#1](https://github.com/gustavonm20/Sistema-de-comandas/issues/1), [#3](https://github.com/gustavonm20/Sistema-de-comandas/issues/3), [#10](https://github.com/gustavonm20/Sistema-de-comandas/issues/10), [#19](https://github.com/gustavonm20/Sistema-de-comandas/issues/19) |
| Catálogo persistente | Cadastro, busca, edição e estado testados no MySQL | Revisar interface e aceitar os critérios da issue original | [#11](https://github.com/gustavonm20/Sistema-de-comandas/issues/11) |
| Ciclo de comandas | Número reutilizável, itens, total e histórico de preço | Resolver cancelamento vazio, reajuste durante atendimento e corrida com fechamento | [#12](https://github.com/gustavonm20/Sistema-de-comandas/issues/12), [#21](https://github.com/gustavonm20/Sistema-de-comandas/issues/21) |
| Pagamento e histórico | Registro local, troco, venda única e rollback testados | Validar formulários/filtros e transação com requisições simultâneas | [#13](https://github.com/gustavonm20/Sistema-de-comandas/issues/13), [#21](https://github.com/gustavonm20/Sistema-de-comandas/issues/21) |
| Operação e caixa | Abertura, bloqueio e conferência sequenciais testados | Bloquear criação concorrente de pedido no encerramento e revisar UX | [#14](https://github.com/gustavonm20/Sistema-de-comandas/issues/14), [#5](https://github.com/gustavonm20/Sistema-de-comandas/issues/5), [#6](https://github.com/gustavonm20/Sistema-de-comandas/issues/6), [#7](https://github.com/gustavonm20/Sistema-de-comandas/issues/7) |
| Resumos | Dia, semana e mês consultam vendas persistidas | Selecionar operação/período, comparar bases equivalentes, tratar ausência de dados e gráfico fora de 08h–20h | [#15](https://github.com/gustavonm20/Sistema-de-comandas/issues/15), [#8](https://github.com/gustavonm20/Sistema-de-comandas/issues/8) |
| Integração visual | Marca, 15 templates, CSS, JS, 16 frames hi-fi e 10 low-fi | Completar conexões do Figma e revisar teclado, contraste, responsividade e estados | [#2](https://github.com/gustavonm20/Sistema-de-comandas/issues/2), [#9](https://github.com/gustavonm20/Sistema-de-comandas/issues/9), [#16](https://github.com/gustavonm20/Sistema-de-comandas/issues/16) |
| Verificação e acesso | Testes locais, integração MySQL e CI aprovados | Concorrência, migrations, revisão Windows, política de lint e autenticação/CSRF | [#17](https://github.com/gustavonm20/Sistema-de-comandas/issues/17), [#24](https://github.com/gustavonm20/Sistema-de-comandas/issues/24) |
| Extensões posteriores | Estoque descrito, sem implementação | Definir unidades, momento da baixa, ajustes e estornos antes de modelar | [#20](https://github.com/gustavonm20/Sistema-de-comandas/issues/20) |

A próxima sequência prática é revisar a entrega do catálogo #11 e corrigir o protocolo de concorrência da #21, coordenado com #14. Para qualquer banco com dados anteriores, a #19 é um pré-requisito. Antes de acesso externo, concluir #24. Estoque não deve impedir a aceitação do catálogo ou a consolidação básica do atendimento.

O protótipo terminal permanece como aprendizado; não recebe novas funções para substituir a web. Não há compromisso com integração bancária, emissão fiscal, múltiplas lojas ou aplicativo móvel. Tema escuro já tem código e deve ser revisado, não anunciado como algo ainda inexistente.

As regras de movimentação e as alterações pendentes no GitHub Projects estão em [docs/KANBAN.md](docs/KANBAN.md). Critérios satisfeitos e entrega aceita são necessários antes de marcar algo como concluído.
