# Orientações para manutenção do FluxoPag

Estas orientações se aplicam ao repositório inteiro. Preserve instruções mais específicas que venham a existir nos diretórios.

## Escopo e linguagem

- Use Python, Flask, HTML, CSS, JavaScript puro e SQL MySQL. Não acrescente biblioteca estrutural, banco ou linguagem de aplicação para fins de apresentação.
- Identificadores próprios em português brasileiro, sem acentos para facilitar o uso. Interface, documentação, tarefas, comunicação e registros de alteração concisos em português brasileiro.
- Preserve `protótipo-inicial.py`, o histórico Git, a compatibilidade dos dados existentes e a marca. `legado/terminal-json` é histórico e não é importado pela web.
- Compare artefatos e registre origem antes de integrar. Não trate nome de ZIP, planejamento ou tela Figma como prova de implementação.

## Arquivos e comandos

- Entrada: `python aplicacao.py`; configuração: `.env`, lida ao lado de `aplicacao.py`.
- Regras e SQL: `servicos.py`; conexão: `banco.py`; utilitários: `utilitarios.py`.
- Inicialização: `python inicializar_banco.py --usuario root --solicitar-senha`, somente banco vazio. Não aplicar estrutura inteira sobre banco antigo nem apagar dados para fazê-lo funcionar.
- Testes: `python -m unittest discover -s testes -p 'teste_*.py' -v`.
- MySQL real: `EXECUTAR_TESTES_MYSQL=1` e banco descartável com prefixo `fluxopag_teste_`; a suíte remove seus registros. Ver `documentacao/TESTES.md`.
- Legado, dentro de `legado/terminal-json`: `python -m unittest discover -p "teste_*.py" -v`.
- Ligações locais: `python ferramentas/verificar_documentacao.py`; arquivos novos precisam estar adicionados ao Git para entrar na verificação.

## Invariantes e limites

- Cartão tem quatro dígitos ASCII, não exige cliente e admite um pedido aberto; fechar preserva dados e libera o número.
- Produtos inativos não entram em novos consumos; preço/nome/categoria dos itens são cópias históricas.
- Use `Decimal` e SQL parametrizado. Banco aceita preço zero, serviço exige positivo; registre a divergência, não altere regra silenciosamente.
- Fechamento precisa ser atômico. O código atual ainda tem corridas entre itens/fechamento e pedido/operação: não descreva essas garantias como resolvidas sem teste simultâneo.
- Registrar meio de pagamento não significa processar transação com provedor.
- Conta do estabelecimento não é autenticação. CSRF/autenticação e a evolução geral das migrações estão pendentes; não publicar uma aplicação como pronta para produção.

## Entrega e evidência

Atualize documentos existentes, matriz de situação, planejamento e tarefa pertinente. Preserve caminhos e mantenha ligações relativos de arquivos/imagens. Diferencie captura de tela de implementação e prévia de projeto visual. Não invente testes, cobertura, versão, licença, responsável, prazo ou resultado de integração contínua.

Trabalhe em ramo e abra solicitação de integração com validação e lacunas. Não force-push, reescreva história ou faça integração sem autorização. Não encerre tarefas apenas por abrir solicitação de integração. O Markdown do Kanban não altera o Projects: registre exatamente qualquer operação remota não aplicada.

## Tradução e compatibilidade

O MySQL continua sendo o banco do projeto. Mantenha a sintaxe obrigatória das linguagens, APIs, nomes de dependências e arquivos reconhecidos por ferramentas (`README.md`, `AGENTS.md`, `.github/workflows`, `.github/ISSUE_TEMPLATE` e `.github/pull_request_template.md`). Os módulos `compatibilidade.py` e os testes de migração contêm as grafias antigas necessárias para ler os dados anteriores. Não traduza contratos externos, referências históricas nem valores pessoais salvos.

`migrar_banco.py` copia apenas a versão Flask anterior de nove tabelas para um banco novo. Não altera a origem e recusa destino ocupado. Os testes de migração consultam o registro Git anterior; mantenha o histórico disponível. Mudanças em nomes persistidos devem ser acompanhadas por conversão explícita e testes de preservação.
