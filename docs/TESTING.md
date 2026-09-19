# Verificação e limites

[Índice](README.md) · [Estado das funcionalidades](STATUS.md)

## Evidência de 17/09/2026

A [execução 35213699602 do GitHub Actions](https://github.com/gustavonm20/Sistema-de-comandas/actions/runs/35213699602), no commit `2adc6900b09f988ef975e285207b57dcab842e10`, terminou com sucesso. O job usou Python 3.12 e **MySQL Server 8.4.11 real**, em serviço isolado. Executou inicialização, **36 testes da aplicação (12 de integração MySQL)** e **6 testes do terminal JSON**. Não houve substituição por SQLite ou banco em memória.

| Grupo | O que foi executado | Limite |
| --- | --- | --- |
| Utilitários e validação | Dinheiro, valores não finitos, limites, calendário, quatro dígitos e entradas inválidas | Não substitui testes SQL |
| Flask local | Compilação Jinja, arquivos estáticos e erro de banco sem detalhes expostos | Test client, sem navegador real |
| Catálogo MySQL | Cadastro, busca, alteração, ativação e persistência após reconectar | Revisão humana de formulários ainda necessária |
| Pedidos e pagamento | Exclusividade sequencial, itens, inatividade, snapshots, troco, reutilização e rejeição de segundo fechamento | Não exerce disputas simultâneas |
| Transação | Falha simulada na auditoria após inserir venda causa rollback de toda a operação | Não é teste de queda física do servidor |
| Caixa | Operação única, bloqueio com pedido aberto, dinheiro esperado e justificativa de diferença | Sem sangrias, reabertura ou concorrência |
| SQL | Constraints, FKs, sete views, inicializador que recusa banco existente e reexecução do schema atual | Não comprova migration de schema antigo |
| Resumos e páginas | Consultas de dia/semana/mês e 15 GETs Flask retornando 200 com MySQL | Não verifica aparência, JavaScript nem todos os POSTs por HTTP |
| Terminal histórico | Seis testes próprios de lógica/JSON | Independente da aplicação web |

A [primeira execução](https://github.com/gustavonm20/Sistema-de-comandas/actions/runs/35176248455) falhou em duas consultas com `ONLY_FULL_GROUP_BY`. A correção separou agregação e formatação em subconsultas; o modo estrito foi mantido. Registrar essa falha explica uma correção concreta, sem apresentar uma suíte verde fictícia.

No ambiente local de consolidação, sem MySQL instalado, passaram 24 testes da aplicação e os 12 de banco foram explicitamente ignorados; os seis testes históricos também passaram. A integração foi verificada no serviço MySQL do Actions, não nesse ambiente local.

A inspeção de `app.url_map` confirmou 21 regras (20 da aplicação e arquivos estáticos). O protótipo inicial teve sintaxe e abertura/saída do menu verificadas.

## Executar sem MySQL

Na raiz, com as dependências instaladas:

```powershell
python -m unittest discover -s tests -v
python scripts/check_docs.py
```

Sem `RUN_MYSQL_TESTS=1`, a saída informa `skipped` para os testes do banco. Não confundir essa execução com validação de persistência. `check_docs.py` verifica destinos locais, imagens e âncoras de arquivos Markdown versionados; não acessa links externos nem valida o significado dos textos.

## Executar integração real

Use um banco **descartável** cujo nome comece por `fluxopag_test_`. A suíte apaga registros das tabelas de negócio em cada teste. Nunca use o banco de trabalho.

Em outro terminal PowerShell, configure o ambiente de teste; esses valores prevalecem sobre `.env`:

```powershell
$env:MYSQL_DATABASE = "fluxopag_test_local"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = Read-Host "Senha do MySQL local" -MaskInput
$env:RUN_MYSQL_TESTS = "1"
python initialize_database.py
python -m unittest discover -s tests -v
Remove-Item Env:RUN_MYSQL_TESTS, Env:MYSQL_DATABASE, Env:MYSQL_USER, Env:MYSQL_PASSWORD
```

`-MaskInput` exige PowerShell 7.1+. No Windows PowerShell 5.1, use um usuário de teste e configure a senha em um `.env` local temporário ignorado pelo Git; não a inclua no histórico do terminal. Outra opção é executar a mesma suíte pelo workflow. Se o banco de testes já estiver inicializado, pule o inicializador: a suíte faz a limpeza controlada. O prefixo é verificado antes de qualquer `DELETE`.

No Linux/macOS, exporte as mesmas variáveis e use `read -rs MYSQL_PASSWORD; export MYSQL_PASSWORD` para não exibir a senha. Mantenha Python e MySQL no mesmo fuso; a CI configura `America/Sao_Paulo` para ambos.

Para o histórico:

```powershell
cd legacy/terminal-json
python -m unittest discover -p "test_*.py" -v
```

## CI e verificações ainda pendentes

[verify.yml](../.github/workflows/verify.yml) instala as três dependências, sobe MySQL, inicializa banco isolado e executa aplicação, legado e links. Usa `unittest`, já presente nos artefatos; não exige adotar Pytest apenas por constar de um plano antigo. O workflow não configura proteção da branch: tornar checks obrigatórios é uma configuração administrativa separada.

Ainda faltam: conexões concorrentes (#21, #14), migrations com dados antigos (#19), autenticação/CSRF (#24), acessibilidade e navegação real em computador/tablet (#16), revisão do setup no Windows, testes completos dos filtros/POSTs HTTP e cenários de períodos sem dados/virada de ano (#15, #17). Não existe percentual de cobertura medido nem benchmark publicado.
