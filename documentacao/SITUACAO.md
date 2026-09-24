# Estado do projeto e evidências

[Índice](README.md) · [Testes](TESTES.md)

Revisão: **24/09/2026**. A consolidação original foi integrada pela [solicitação de integração #25](https://github.com/gustavonm20/Sistema-de-comandas/pull/25). A versão atual mantém MySQL, preserva no próprio repositório os artefatos necessários à migração e possui [41 testes da aplicação e oito históricos aprovados](https://github.com/gustavonm20/Sistema-de-comandas/actions/runs/35426696558). A integração disponibiliza os fontes; não encerra requisitos ainda pendentes.

## Como ler os estados

- **Verificado:** existe uma execução identificada para o comportamento descrito.
- **Implementado, por verificar:** há código, mas falta a execução pertinente, para o cenário em questão.
- **Parcial:** há código ou projeto visual, porém requisitos relevantes ainda não são atendidos.
- **Só projeto visual:** existe representação visual sem comportamento equivalente comprovado no aplicativo.
- **Planejado:** consta do escopo ou lista de pendências, sem implementação localizada.

Um teste estrutural, uma simulação ou um teste do terminal JSON não comprova integração MySQL. A [verificação](TESTES.md) registra essa separação.

| Recurso | Estado do código | Evidência principal | Execução | Projeto visual / tarefa |
| --- | --- | --- | --- | --- |
| Protótipo inicial | Artefato histórico preservado; catálogo em memória, outros menus são esboços | [protótipo-inicial.py](../protótipo-inicial.py) | Sintaxe e abertura/saída do menu | Treino anterior |
| Evolução terminal JSON | Histórico; lógica e persistência de arquivo | [legado/terminal-json](../legado/terminal-json/README.md) | 8 testes aprovados, incluindo leitura do formato antigo | Não é a aplicação MySQL |
| Conversão de dinheiro e períodos | Verificado nos casos da suíte local | [utilitarios.py](../utilitarios.py), [test_utilitarios.py](../testes/teste_utilitarios.py) | 11 testes unitários | #17 |
| Catálogo persistente | Verificado nos cenários da suíte MySQL; revisão humana pendente | `validar_produto`, `criar_produto`, `listar_produtos`, `atualizar_produto`, `alterar_situacao_produto` em [servicos.py](../servicos.py) | cadastro, consulta, edição e desativação, filtros e reconexão aprovados em MySQL real | Alta fidelidade e baixa fidelidade / #11 |
| Cartões e abertura de comandas | Parcial; valida operação, disponibilidade e número | `criar_cartao_comanda`, `criar_pedido`; `UNIQUE(id_cartao_aberto)` | Número, operação requerida e exclusividade sequencial verificados | #12 |
| Itens e preço histórico | Parcial; cópias históricas e bloqueio de produto inativo; concorrência pendente | `adicionar_item_pedido`, `atualizar_item_pedido`, `remover_item_pedido`, [estrutura](../banco_dados/estrutura.sql) | Itens, quantidade, inatividade e cópias históricas verificados em MySQL | #11, #12, #21 |
| Fechamento e histórico | Parcial; transação, venda única, troco e consultas presentes | `fechar_pedido`, `listar_vendas`, `obter_venda` | Reversão, venda única sequencial, troco e reutilização verificados | #13, #21 |
| Processamento financeiro externo | Fora do escopo atual; exige nova decisão | Não há provedor, webhook ou confirmação bancária | Não se aplica | Sem entrega afirmada |
| Dados do estabelecimento | Implementado; alteração dos dados ainda sem teste específico | `obter_estabelecimento`, `atualizar_estabelecimento`, [conta.html](../modelos/conta.html) | Modelo e GET com MySQL testados; POST da conta não exercitado | Conta alta fidelidade / #10, #24 |
| Autenticação, senha e saída | Só projeto visual / planejado no código | Não há rotas de autenticação | Não implementado | Controles visuais no Figma / #24 |
| Abertura e conferência do caixa | Parcial; valores, divergência e bloqueio presentes; corridas pendentes | `abrir_operacao`, `fechar_operacao`, `operacoes_diarias` | Caixa, divergência e bloqueio sequencial aprovados em MySQL | Alta fidelidade existe, baixa fidelidade específico falta / #5–#7, #14 |
| Resumos diário, semanal e mensal | Parcial; páginas por parâmetro e SQL presentes; não selecionam operação encerrada | `/resumos?periodo=diario`, `semanal`, `mensal`, `obter_resumo` | Limites de calendário e consultas dos três períodos testados | Três quadros alta fidelidade / #8, #15 |
| Disposição visual, tema e navegação | Implementado; revisão visual e de acessibilidade parcial | [modelos](../modelos/), [CSS](../estaticos/css/estilo.css), [JS](../estaticos/js/principal.js) | Modelos, recursos e 15 GETs com MySQL testados; sem navegação completa no navegador | #16 |
| Estrutura e visões | Inicialização e consultas verificadas em MySQL real | [banco_dados/estrutura.sql](../banco_dados/estrutura.sql), nove tabelas e sete visões | MySQL 8.4.11: inicialização, restrições, FKs e sete visões aprovadas | #10, #19 |
| Auditoria básica | Implementada; ator fixo `administrador-local` | `registrar_auditoria`, `registros_auditoria` | Reversão com falha na auditoria testado; não identifica usuário autenticado | #24 |
| Conversão da versão Flask anterior | Verificada para nove tabelas InnoDB | [migrar_banco.py](../migrar_banco.py), [compatibilidade](../compatibilidade.py) | Quatro cenários MySQL aprovados; origem preservada | #19 |
| Evolução geral do banco e estoque | Planejados | Outras variantes antigas, versões incrementais e saldo de estoque | Não implementados | #19, #20 |
| integração contínua | Rotina executado com sucesso | [verificar.yml](../.github/workflows/verificar.yml) | Resultado remoto registrado em [TESTES.md](TESTES.md) | #17 |

## Pendências que impedem afirmar maturidade operacional

1. Revisar os fluxos interativos e os POSTs ainda não exercitados, além da instalação no Windows. A integração MySQL já passou na [execução 35213699602](https://github.com/gustavonm20/Sistema-de-comandas/actions/runs/35213699602).
2. Evitar disputa entre edição de itens e fechamento, e entre abertura de comanda e encerramento da operação (#21, #14).
3. Definir o comportamento quando o preço muda entre duas inclusões do mesmo produto: o código conserva a primeira linha e o primeiro preço (#1, #12).
4. Ampliar a conversão para outras estruturas e migrações incrementais (#19), além de autenticação e CSRF (#24).
5. Alinhar resumo por operação, períodos comparados e seleção de datas (#15).
6. Completar as conexões de caixa e os esboços de telas correspondentes no Figma (#5–#9).
