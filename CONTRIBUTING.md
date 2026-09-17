# Como contribuir com o FluxoPag

Comece pelo [README](README.md), pelo [setup](docs/SETUP.md) e pela [matriz de evidências](docs/STATUS.md). Consulte a issue existente antes de abrir outra; catálogo é #11, transação é #21 e migrations são #19.

## Fluxo de trabalho

1. Descreva o problema, o comportamento esperado e como verificá-lo em uma issue.
2. Crie uma branch a partir da base acordada. A consolidação atual está em `chore/consolidar-fluxopag`; não misture alterações não relacionadas.
3. Faça mudanças pequenas e commits concisos em português, como `Correção do total da comanda` ou `Documentação da operação diária`, seguindo o histórico do repositório.
4. Execute os testes pertinentes, revise o diff e abra uma PR com evidência e limitações.
5. Mova para revisão quando a entrega estiver pronta; encerre a issue somente após critérios satisfeitos e aceitação/integração. Use `Relacionada a #...` enquanto houver trabalho restante.

Não reescreva commits históricos, force-push ou faça merge sem a autorização aplicável. Não atribua prazos ou responsáveis sem acordo.

## Código e documentação

- Stack: Python, Flask, HTML, CSS, JavaScript puro e SQL MySQL. Dependências devem ter uma necessidade concreta.
- Novos identificadores de aplicação em inglês; interface, documentação, issues e mensagens em português brasileiro.
- Preserve nomes históricos e SQL existentes. O schema atual está em inglês; o nome `comandas_db` é preservado. Mudanças exigem compatibilidade explícita.
- SQL com valores parametrizados. Dinheiro com `Decimal`, nunca `float` como fonte do cálculo financeiro.
- Quatro dígitos, cartão com um pedido aberto, snapshots, inatividade e fechamento atômico são invariantes do domínio.
- Atualize documentos existentes e índice, sem criar guias paralelos sobre o mesmo assunto. Identifique se uma imagem é Figma ou aplicação.
- Não afirme função pronta por existir em um roteiro. Vincule a execução ao commit/CI e documente os limites.

## Verificação

```powershell
python -m unittest discover -s tests -v
python scripts/check_docs.py
```

[Testes com MySQL real](docs/TESTING.md) exigem banco descartável `fluxopag_test_*` e `RUN_MYSQL_TESTS=1`. Sem isso, os testes SQL aparecem como ignorados. Não execute limpeza ou testes destrutivos no banco de trabalho.

Verifique novas regras ou integrações com testes que exercitem o comportamento. Mudanças simples de texto não precisam de testes artificiais. A revisão visual deve incluir estado vazio, erro, foco de teclado e largura reduzida. Não coloque dados reais em screenshots ou seeds.

## Configuração e publicação

`.env`, credenciais, arquivos locais de dados e ambientes virtuais não devem ser commitados. Use `.env.example`. Não exponha o servidor de desenvolvimento enquanto faltarem autenticação e CSRF (#24). Não foi confirmado um canal privado de relato de vulnerabilidades; evite publicar segredos em issues. A definição de um canal apoiado pelo proprietário permanece pendente, sem endereço inventado.

Não existe licença definida no repositório auditado. A escolha cabe ao proprietário; contribuições devem informar a origem de código e assets externos. Não acrescente um arquivo de licença ou badge por suposição.
