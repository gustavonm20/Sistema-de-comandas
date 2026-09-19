<p align="center"><img src="documentacao/imagens/fluxopag-logotipo.png" width="420" alt="FluxoPag — Sistema Ágil de Comandas"></p>

# FluxoPag — Sistema de Comandas

**Do consumo ao fechamento: produtos, comandas numeradas, pagamentos registrados e visão da operação.**

Aplicação em Python e Flask para padarias, restaurantes, cafés e pequenos estabelecimentos. O FluxoPag associa os itens consumidos a uma comanda reutilizável, calcula o total e preserva a venda depois do fechamento.

[Documentação](documentacao/README.md) · [Instalação](documentacao/INSTALACAO.md) · [Projeto visual no Figma](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=0-1) · [Abrir protótipo](https://www.figma.com/proto/Rau8PgbGwiiJwRo9MHgzMW/Comandas?page-id=0%3A1&node-id=12-2&starting-point-node-id=12%3A2) · [Planejamento](PLANEJAMENTO.md) · [Tarefas](https://github.com/gustavonm20/Sistema-de-comandas/issues) · [Kanban existente](https://github.com/users/gustavonm20/projects/2/views/4)

> **Aplicação em desenvolvimento, disponível para execução local.** O código web e a documentação foram integrados à `main` pela [solicitação de integração #25](https://github.com/gustavonm20/Sistema-de-comandas/pull/25). A [verificação anterior com MySQL real](https://github.com/gustavonm20/Sistema-de-comandas/actions/runs/35213699602) passou: 36 testes da aplicação e seis do terminal histórico. Autenticação, proteção CSRF, evolução geral das migrações e segurança sob concorrência ainda precisam de trabalho. Consulte a [matriz de evidências](documentacao/SITUACAO.md) antes de considerar uma funcionalidade concluída.

## Uma operação mais fácil de acompanhar

Durante o atendimento, a equipe precisa saber qual comanda está ocupada, o que foi consumido, quanto deve ser recebido e o que já foi encerrado. Ao final, precisa conferir o dinheiro e consultar os resultados sem perder os atendimentos anteriores.

O objetivo é reunir esse fluxo em uma interface simples: **abrir a operação → atender por comanda → registrar pagamento → conferir o caixa**. A identificação usa um número físico de quatro dígitos; não depende do nome do cliente.

## Como o produto foi pensado

![Prévia autêntica do painel no Figma, com navegação lateral, indicadores e comandas ilustrativas](documentacao/imagens/figma-painel.png)

*Prévia de projeto visual exportada do Figma em 17/09/2026. Valores e textos são ilustrativos; esta imagem não é uma captura da aplicação funcionando. O arquivo ainda contém detalhes a revisar, como indicadores temporários e números de exemplo com três dígitos.*

A fase de Figma tornou a experiência pretendida concreta: estrutura das telas, sequência de tarefas, estados da operação e identidade FluxoPag. O [guia de projeto visual](documentacao/FIGMA.md) explica baixa fidelidade, alta fidelidade, os 16 quadros alta fidelidade encontrados e as diferenças em relação ao código. O ponto de entrada do protótipo foi identificado; a navegação completa ainda precisa de revisão.

## O que existe hoje

| Recurso | Implementação atual | Projeto visual |
| --- | --- | --- |
| Produtos: cadastrar, buscar, editar, ativar/desativar | cadastro, consulta, edição e desativação e persistência verificados com MySQL; revisão visual pendente | Tela alta fidelidade e baixa fidelidade |
| Comandas e itens, total e reutilização | Parcial: fluxo presente; concorrência pendente | Telas principais presentes |
| Pagamento e histórico | Registro local, troco, cópias históricas e reversão verificados; concorrência pendente | Pagamento e histórico presentes |
| Conta e operação diária | Dados do estabelecimento e caixa presentes; sem autenticação | Conta, abertura, bloqueio e conferência presentes; conexões incompletas |
| Resumos de dia, semana e mês | Três visões por URL; consultas presentes; regras de período parcialmente alinhadas | Três telas alta fidelidade; comparativos pendentes |
| Tema claro/escuro e menu adaptável | CSS e JavaScript presentes; revisão visual completa pendente | Prévia principal clara |
| Autenticação, CSRF, migrações e estoque | Planejados; estoque é extensão posterior | Nem toda extensão possui tela verificada |

O pagamento é **registrado pelo atendente**. Não há cobrança de cartão, confirmação bancária de Pix ou integração com adquirente. A [matriz completa](documentacao/SITUACAO.md) associa recursos, arquivos, verificações e tarefas.

## Da lógica ao produto

1. **Terminal:** o arquivo [protótipo-inicial.py](protótipo-inicial.py) preserva o treino inicial de Python, principalmente o catálogo em memória. Uma [evolução histórica do terminal](legado/terminal-json/README.md), recuperada de outro ZIP, usa JSON e tem testes próprios.
2. **Figma:** esboços de telas e telas detalhadas planejam navegação, estados e identidade visual. Não constituem evidência de testes com clientes.
3. **MySQL:** a estrutura representa entidades, relacionamentos, preços históricos e restrições de integridade.
4. **Web:** a versão recuperada de `FluxoPag-Flask-MySQL.zip` reúne Flask, modelos, estilos, interações e acesso SQL. A consolidação corrige incompatibilidades e torna o código navegável no GitHub.

Consulte a [origem dos arquivos e decisões de integração](documentacao/ORIGEM_ARQUIVOS.md).

## Tecnologias e estrutura

| Tecnologia | Uso no projeto |
| --- | --- |
| Python 3.10+ | Validação, regras de negócio, dinheiro com `Decimal` e testes com `unittest` |
| Flask e Jinja | Rotas, formulários, mensagens e geração das páginas HTML |
| HTML e CSS | Estrutura das telas, disposição visual e temas |
| JavaScript | Menu, tema, confirmação e prévia de troco |
| SQL e MySQL 8.0.16+ / 8.4 | Persistência, relações, restrições, visões e transações |
| mysql-connector-python | Conexões e consultas SQL parametrizadas |
| python-dotenv | Leitura do `.env` local; variáveis do ambiente têm precedência |

O navegador envia formulários a [aplicacao.py](aplicacao.py); [servicos.py](servicos.py) valida e consulta o banco por [banco.py](banco.py). O Flask entrega os [modelos HTML](modelos/) com os [arquivos estáticos](estaticos/). Não há API REST separada nem ORM.

| Caminho | Responsabilidade |
| --- | --- |
| [aplicacao.py](aplicacao.py), [servicos.py](servicos.py), [utilitarios.py](utilitarios.py) | Entrada web, regras e utilitários |
| [banco_dados/](banco_dados/) | Estrutura atual, exemplos e estrutura histórico preservado |
| [inicializar_banco.py](inicializar_banco.py) | Inicialização protegida para banco vazio |
| [modelos/](modelos/), [estaticos/](estaticos/) | Interface e recursos recuperados |
| [testes/](testes/) | Verificações locais e integração optativa com MySQL real |
| [documentacao/](documentacao/README.md) | Referência técnica, produto, projeto visual e gestão |
| [legado/terminal-json/](legado/terminal-json/README.md) | Protótipo anterior, isolado da aplicação web |

Veja a [arquitetura](documentacao/ARQUITETURA.md), o [modelo de dados](documentacao/BANCO_DADOS.md) e as [rotas](documentacao/ROTAS.md).

## Executar localmente

Você precisa de Python e de um **MySQL Servidor em execução**. O Workbench é a interface de administração; ele não substitui o servidor.

```powershell
git clone https://github.com/gustavonm20/Sistema-de-comandas.git
cd Sistema-de-comandas
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r dependencias.txt
Copy-Item .env.exemplo .env
```

Edite `.env` com as credenciais locais e uma chave gerada com `python -c "import secrets; print(secrets.token_hex(32))"`. O [guia de instalação](documentacao/INSTALACAO.md) mostra como preparar o usuário MySQL, configurar um banco vazio e resolver problemas do PowerShell.

```powershell
python inicializar_banco.py --usuario root --solicitar-senha
python aplicacao.py
```

Cadastre produtos e inicie a operação em **Conta e operação**. O inicializador recusa bancos que já contêm tabelas: **a estrutura novo não é uma migração do banco antigo**. Preserve seus dados e consulte [compatibilidade](documentacao/BANCO_DADOS.md).

Linux/macOS usam `python3 -m venv .venv`, `source .venv/bin/activate` e `cp .env.exemplo .env`; o restante é igual. Para o treino inicial, execute separadamente `python "protótipo-inicial.py"`.

```powershell
python -m unittest discover -s testes -p 'teste_*.py' -v
python ferramentas/verificar_documentacao.py
```

Sem `EXECUTAR_TESTES_MYSQL=1`, os testes de banco são explicitamente ignorados. O [guia de verificação](documentacao/TESTES.md) explica a execução isolada, os resultados obtidos e os limites.

## Regras e limites importantes

- A comanda possui, obrigatoriamente, quatro dígitos e só pode ter um atendimento aberto por vez.
- O fechamento libera o número e preserva pedido, itens e venda.
- Produtos inativos não entram em novos consumos; os itens conservam o preço registrado.
- A aplicação exige preço positivo; o banco mantém a restrição histórica `>= 0`. Produtos gratuitos ainda dependem de decisão explícita.
- A operação precisa estar aberta; o encerramento verifica comandas pendentes e exige justificativa para divergência de caixa.
- Os bloqueios estão no código, mas disputas entre requisições simultâneas ainda precisam ser tratadas e verificadas.
- Resumos atuais seguem a data da venda; o resumo de uma operação encerrada é uma pendência de alinhamento.

Leia as [regras e casos de borda](documentacao/REGRAS_NEGOCIO.md). Não há implantação desta versão Flask apresentada como pronta para produção.

## Próximos passos e participação

A prioridade é revisar e aceitar o catálogo da [tarefa #11](https://github.com/gustavonm20/Sistema-de-comandas/issues/11), corrigir a transação sob concorrência na #21 e preparar migrações antes de usar dados existentes. O [planejamento](PLANEJAMENTO.md) mantém as fases e dependências; a [política do Kanban](documentacao/QUADRO_TAREFAS.md) distingue propostas de alterações efetivamente aplicadas ao quadro.

[Como contribuir](CONTRIBUICAO.md) · [Competências demonstradas](documentacao/COMPETENCIAS.md) · [Histórico de mudanças](ALTERACOES.md) · [Orientações para agentes](AGENTS.md)

## Projeto em português brasileiro

O código próprio, os nomes de arquivos, as rotas, os modelos HTML, os estilos, as configurações e a estrutura SQL usam português brasileiro. O **MySQL foi mantido**. Palavras reservadas, nomes de bibliotecas e contratos exigidos pelas ferramentas conservam a grafia original. As referências em inglês necessárias para ler dados antigos estão isoladas na compatibilidade e em seus testes.

Se já usa a versão anterior, siga a [conversão do banco](documentacao/BANCO_DADOS.md#compatibilidade-e-evolução) antes de iniciar esta versão. A conversão faz uma cópia para outro banco MySQL e preserva a origem. O protótipo JSON também lê o formato anterior e grava no novo caminho, sem sobrescrever o arquivo original.
