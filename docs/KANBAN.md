# Kanban e organização do GitHub

[Índice](README.md) · [Roadmap](../ROADMAP.md) · [Quadro existente](https://github.com/users/gustavonm20/projects/2/views/4)

O quadro de referência é o [FluxoPag Kanban — Projects 2, visão 4](https://github.com/users/gustavonm20/projects/2/views/4). Nenhum segundo quadro foi criado.

## O que foi aplicado e o que depende de acesso

As descrições das 20 issues ativas foram reconciliadas com código, design e testes, incluindo #11. A #20 passou de MVP para extensão; #24 foi criada para acesso e formulários. Foram reutilizadas as labels existentes `bug`, `enhancement` e `documentation`. Não há encerramentos novos nem atribuição de responsáveis/prazos.

A integração GitHub disponível permite arquivos, commits, PRs e issues, mas não expõe edição de Projects, criação de labels/milestones ou configuração do repositório. O acesso ao quadro pelo navegador sem sessão retornou 404; isso **não demonstra que o quadro foi excluído**. Sua configuração e seus itens não puderam ser inspecionados. Portanto, as operações abaixo são **pendentes**, não alterações já aplicadas ao Projects.

Não foram encontrados milestones na consulta pública da revisão. As nove labels padrão foram consultadas; nenhuma label existente foi apagada. Área e prioridade foram registradas nos corpos das issues enquanto os campos nativos não estão disponíveis.

## Política de fluxo

| Status | Condição para entrar | Condição para sair |
| --- | --- | --- |
| Backlog | Escopo futuro ou decisão/dependência ainda aberta | Critérios e dependências suficientes para iniciar |
| A fazer | Trabalho delimitado e pronto para ser escolhido | Desenvolvimento realmente iniciado |
| Em andamento | Alteração ativa, vinculada a issue/branch | Entrega concreta pronta para revisão |
| Em revisão | Código/documento entregue e aguardando aceitação | Critérios satisfeitos e integração ou aceitação explícita |
| Concluído | Entrega aceita com evidência | Reabrir apenas se houver regressão/escopo justificável |

Uma PR aberta não encerra automaticamente uma issue. Duplicada, cancelada e substituída não significam funcionalidade concluída. A #4 permanece fechada como duplicada da #2, fora das métricas de entrega. PRs #18, #22, #23 e #25 foram integradas e são histórico concluído, sem tornar o escopo atual das issues automaticamente pronto.

## Configuração exata pendente

1. Abrir **o Projects 2 existente**, inspecionar campos/opções e itens antes de editar; preservar opções equivalentes e histórico.
2. Mapear o campo `Status` para **Backlog, A fazer, Em andamento, Em revisão, Concluído**, reaproveitando opções existentes. Não reinicializar o quadro.
3. Reutilizar ou criar `Prioridade` com **Alta, Normal** e `Área` com **Produto, Design, Aplicação, Dados, Qualidade**, se esses campos trouxerem filtros úteis. Preferir o campo de milestone das issues a um campo duplicado.
4. Criar/reutilizar os milestones **Base consolidada**, **Atendimento e caixa**, **Interface e resumos**, **Qualidade e acesso**, **Extensões posteriores**, sem prazo. Atribuir conforme a tabela.
5. Adicionar as issues reais abaixo somente se ainda não forem itens. Preencher status, prioridade e área; conferir a evidência antes de movimentar.
6. Vincular a [PR #25](https://github.com/gustavonm20/Sistema-de-comandas/pull/25) e marcar seu item como **Concluído**: a integração à `main` foi confirmada em 17/09/2026. Manter as issues de funcionalidades nos estados da tabela até satisfazer seus próprios critérios. Preservar os itens históricos das PRs #18/#22/#23, quando já presentes.
7. Para labels de área/prioridade, preferir os campos do Projects. Se filtros no repositório exigirem labels, criar apenas as correspondentes necessárias; não duplicar toda a taxonomia sem necessidade.

| Issue | Status proposto | Prioridade | Área | Milestone proposto | Label aplicada |
| --- | --- | --- | --- | --- | --- |
| [#1](https://github.com/gustavonm20/Sistema-de-comandas/issues/1) | A fazer | alta | produto | Base consolidada | `documentation` |
| [#2](https://github.com/gustavonm20/Sistema-de-comandas/issues/2) | Backlog | normal | design | Interface e resumos | `enhancement` |
| [#3](https://github.com/gustavonm20/Sistema-de-comandas/issues/3) | Em revisão | alta | aplicação | Base consolidada | `enhancement` |
| [#5](https://github.com/gustavonm20/Sistema-de-comandas/issues/5) | A fazer | normal | design | Interface e resumos | `enhancement` |
| [#6](https://github.com/gustavonm20/Sistema-de-comandas/issues/6) | A fazer | normal | design | Interface e resumos | `enhancement` |
| [#7](https://github.com/gustavonm20/Sistema-de-comandas/issues/7) | A fazer | normal | design | Interface e resumos | `enhancement` |
| [#8](https://github.com/gustavonm20/Sistema-de-comandas/issues/8) | Backlog | normal | design | Interface e resumos | `enhancement` |
| [#9](https://github.com/gustavonm20/Sistema-de-comandas/issues/9) | A fazer | normal | design | Interface e resumos | `enhancement` |
| [#10](https://github.com/gustavonm20/Sistema-de-comandas/issues/10) | A fazer | alta | dados | Base consolidada | `enhancement` |
| [#11](https://github.com/gustavonm20/Sistema-de-comandas/issues/11) | Em revisão | alta | aplicação | Base consolidada | `enhancement` |
| [#12](https://github.com/gustavonm20/Sistema-de-comandas/issues/12) | A fazer | alta | aplicação | Atendimento e caixa | `enhancement` |
| [#13](https://github.com/gustavonm20/Sistema-de-comandas/issues/13) | A fazer | alta | aplicação | Atendimento e caixa | `enhancement` |
| [#14](https://github.com/gustavonm20/Sistema-de-comandas/issues/14) | A fazer | alta | aplicação | Atendimento e caixa | `enhancement` |
| [#15](https://github.com/gustavonm20/Sistema-de-comandas/issues/15) | Backlog | normal | aplicação | Interface e resumos | `enhancement` |
| [#16](https://github.com/gustavonm20/Sistema-de-comandas/issues/16) | A fazer | normal | aplicação | Interface e resumos | `enhancement` |
| [#17](https://github.com/gustavonm20/Sistema-de-comandas/issues/17) | A fazer | alta | qualidade | Qualidade e acesso | `enhancement` |
| [#19](https://github.com/gustavonm20/Sistema-de-comandas/issues/19) | A fazer | alta | dados | Base consolidada | `enhancement` |
| [#20](https://github.com/gustavonm20/Sistema-de-comandas/issues/20) | Backlog | normal | dados | Extensões posteriores | `enhancement` |
| [#21](https://github.com/gustavonm20/Sistema-de-comandas/issues/21) | A fazer | alta | dados | Atendimento e caixa | `bug` |
| [#24](https://github.com/gustavonm20/Sistema-de-comandas/issues/24) | Backlog | alta | aplicação | Qualidade e acesso | `enhancement` |

Não há trabalho marcado como Em andamento só por existir no plano. O código de #3 e #11 está na `main`, mas ainda há revisão manual de ambiente/interface nos seus critérios; as demais questões também têm lacunas relevantes. A PR de consolidação não substitui esses itens.

## Metadados do repositório pendentes

Aplicar quando houver ferramenta/permissão para configurações:

- **Descrição:** `FluxoPag — Sistema de Comandas em Python, Flask e MySQL para pequenos estabelecimentos. Produtos, atendimentos e pagamentos registrados; aplicação em evolução.`
- **Topics:** `python`, `flask`, `mysql`, `html`, `css`, `javascript`, `comandas`, `fluxopag`.
- **Website/reference:** `https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=0-1` — identificado no README como **referência de design**, sem sugerir implantação da aplicação.
- **Checks obrigatórios:** avaliar `python-and-mysql` na proteção da branch após revisar as permissões e o fluxo do proprietário. O workflow sozinho não bloqueia merge.

A decisão de licença e um canal privado suportado para relatos de segurança também pertencem ao proprietário; esta organização não cria endereço de contato, versão suportada ou licença fictícia.
