# Como contribuir com o FluxoPag

Comece pelo [README](README.md), pela [instalação](documentacao/INSTALACAO.md) e pela [matriz de evidências](documentacao/SITUACAO.md). Consulte a tarefa existente antes de abrir outra; catálogo é #11, transação é #21 e migrações são #19.

## Fluxo de trabalho

1. Descreva o problema, o comportamento esperado e como verificá-lo em uma tarefa.
2. Crie um ramo a partir da `main` atualizada; não misture alterações não relacionadas.
3. Faça mudanças pequenas e registros de alteração concisos em português, como `Correção do total da comanda` ou `Documentação da operação diária`, seguindo o histórico do repositório.
4. Execute os testes pertinentes, revise o comparação das alterações e abra uma solicitação de integração com evidência e limitações.
5. Mova para revisão quando a entrega estiver pronta; encerre a tarefa somente após critérios satisfeitos e aceitação/integração. Use `Relacionada a #...` enquanto houver trabalho restante.

Não reescreva registros de alteração históricos, force-push ou faça integração sem a autorização aplicável. Não atribua prazos ou responsáveis sem acordo.

## Código e documentação

- Tecnologias: Python, Flask, HTML, CSS, JavaScript puro e SQL MySQL. Dependências devem ter uma necessidade concreta.
- Identificadores próprios da aplicação em português brasileiro; interface, documentação, tarefas e mensagens em português brasileiro.
- Preserve o histórico Git. A estrutura usa nomes em português; mudanças em dados persistidos exigem compatibilidade explícita. A cópia da versão anterior é feita por `migrar_banco.py`.
- SQL com valores parametrizados. Dinheiro com `Decimal`, nunca `float` como fonte do cálculo financeiro.
- Quatro dígitos, cartão com um pedido aberto, cópias históricas, inatividade e fechamento atômico são invariantes do domínio.
- Atualize documentos existentes e índice, sem criar guias paralelos sobre o mesmo assunto. Identifique se uma imagem é Figma ou aplicação.
- Não afirme função pronta por existir em um roteiro. Vincule a execução ao registro de alteração/integração contínua e documente os limites.

## Verificação

```powershell
python -m unittest discover -s testes -p 'teste_*.py' -v
python ferramentas/verificar_documentacao.py
```

[Testes com MySQL real](documentacao/TESTES.md) exigem banco descartável `fluxopag_teste_*` e `EXECUTAR_TESTES_MYSQL=1`. Sem isso, os testes SQL aparecem como ignorados. Não execute limpeza ou testes destrutivos no banco de trabalho.

Verifique novas regras ou integrações com testes que exercitem o comportamento. Mudanças simples de texto não precisam de testes artificiais. A revisão visual deve incluir estado vazio, erro, foco de teclado e largura reduzida. Não coloque dados reais em capturas de tela ou dados iniciais.

## Configuração e publicação

`.env`, credenciais, arquivos locais de dados e ambientes virtuais não devem ser versionados. Use `.env.exemplo`. Não exponha o servidor de desenvolvimento enquanto faltarem autenticação e CSRF (#24). Não foi confirmado um canal privado de relato de vulnerabilidades; evite publicar segredos em tarefas. A definição de um canal apoiado pelo proprietário permanece pendente, sem endereço inventado.

Não existe licença definida no repositório auditado. A escolha cabe ao proprietário; contribuições devem informar a origem de código e recursos externos. Não acrescente um arquivo de licença ou selo por suposição.
