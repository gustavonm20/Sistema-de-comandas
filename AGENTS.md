# Orientações para manutenção do FluxoPag

Estas orientações se aplicam ao repositório inteiro. Preserve instruções mais específicas que venham a existir nos diretórios.

## Escopo e linguagem

- Use Python, Flask, HTML, CSS, JavaScript puro e SQL MySQL. Não acrescente framework, banco ou linguagem de aplicação para fins de apresentação.
- Novos identificadores em inglês. Interface, documentação, issues, comunicação e commits concisos em português brasileiro.
- Preserve `protótipo-inicial.py`, o histórico Git, nomes SQL existentes e a marca. `legacy/terminal-json` é histórico e não é importado pela web.
- Compare artefatos e registre origem antes de integrar. Não trate nome de ZIP, roadmap ou tela Figma como prova de implementação.

## Arquivos e comandos

- Entrada: `python app.py`; configuração: `.env`, lida ao lado de `app.py`.
- Regras e SQL: `services.py`; conexão: `database.py`; utilitários: `utils.py`.
- Inicialização: `python initialize_database.py --user root --ask-password`, somente banco vazio. Não aplicar schema inteiro sobre banco antigo nem apagar dados para fazê-lo funcionar.
- Testes: `python -m unittest discover -s tests -v`.
- MySQL real: `RUN_MYSQL_TESTS=1` e banco descartável com prefixo `fluxopag_test_`; a suíte remove seus registros. Ver `docs/TESTING.md`.
- Legado, dentro de `legacy/terminal-json`: `python -m unittest discover -p "test_*.py" -v`.
- Links locais: `python scripts/check_docs.py`; arquivos novos precisam estar adicionados ao Git para entrar na verificação.

## Invariantes e limites

- Cartão tem quatro dígitos ASCII, não exige cliente e admite um pedido aberto; fechar preserva dados e libera o número.
- Produtos inativos não entram em novos consumos; preço/nome/categoria dos itens são snapshots.
- Use `Decimal` e SQL parametrizado. Banco aceita preço zero, serviço exige positivo; registre a divergência, não altere regra silenciosamente.
- Fechamento precisa ser atômico. O código atual ainda tem corridas entre itens/fechamento e pedido/operação: não descreva essas garantias como resolvidas sem teste simultâneo.
- Registrar meio de pagamento não significa processar transação com provedor.
- Conta do estabelecimento não é login. CSRF/autenticação e migrations estão pendentes; não publicar uma aplicação como pronta para produção.

## Entrega e evidência

Atualize documentos existentes, matriz de status, roadmap e issue pertinente. Preserve caminhos e mantenha links relativos de arquivos/imagens. Diferencie screenshot de implementação e prévia de design. Não invente testes, cobertura, release, licença, assignee, prazo ou resultado de CI.

Trabalhe em branch e abra PR com validação e lacunas. Não force-push, reescreva história ou faça merge sem autorização. Não encerre issues apenas por abrir PR. O Markdown do Kanban não altera o Projects: registre exatamente qualquer operação remota não aplicada.
