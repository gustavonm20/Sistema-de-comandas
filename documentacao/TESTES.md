# Verificação e limites

[Índice](README.md) · [Estado das funcionalidades](SITUACAO.md)

## Evidência de 17/09/2026

A [execução 35213699602 do GitHub Actions](https://github.com/gustavonm20/Sistema-de-comandas/actions/runs/35213699602), no registro de alteração `2adc6900b09f988ef975e285207b57dcab842e10`, terminou com sucesso. O tarefa usou Python 3.12 e **MySQL Servidor 8.4.11 real**, em serviço isolado. Executou inicialização, **36 testes da aplicação (12 de integração MySQL)** e **6 testes do terminal JSON**. Não houve substituição por SQLite ou banco em memória.

| Grupo | O que foi executado | Limite |
| --- | --- | --- |
| Utilitários e validação | Dinheiro, valores não finitos, limites, calendário, quatro dígitos e entradas inválidas | Não substitui testes SQL |
| Flask local | Compilação Jinja, arquivos estáticos e erro de banco sem detalhes expostos | Cliente de teste, sem navegador real |
| Catálogo MySQL | Cadastro, busca, alteração, ativação e persistência após reconectar | Revisão humana de formulários ainda necessária |
| Pedidos e pagamento | Exclusividade sequencial, itens, inatividade, cópias históricas, troco, reutilização e rejeição de segundo fechamento | Não exerce disputas simultâneas |
| Transação | Falha simulada na auditoria após inserir venda causa reversão de toda a operação | Não é teste de queda física do servidor |
| Caixa | Operação única, bloqueio com pedido aberto, dinheiro esperado e justificativa de diferença | Sem sangrias, reabertura ou concorrência |
| SQL | Restrições, FKs, sete visões, inicializador que recusa banco existente e reexecução da estrutura atual | Não comprova migração de estrutura antiga |
| Resumos e páginas | Consultas de dia/semana/mês e 15 GETs Flask retornando 200 com MySQL | Não verifica aparência, JavaScript nem todos os POSTs por HTTP |
| Terminal histórico | Seis testes próprios de lógica/JSON | Independente da aplicação web |

A [primeira execução](https://github.com/gustavonm20/Sistema-de-comandas/actions/runs/35176248455) falhou em duas consultas com `ONLY_FULL_GROUP_BY`. A correção separou agregação e formatação em subconsultas; o modo estrito foi mantido. Registrar essa falha explica uma correção concreta, sem apresentar uma suíte verde fictícia.

No ambiente local de consolidação, sem MySQL instalado, passaram 24 testes da aplicação e os 12 de banco foram explicitamente ignorados; os seis testes históricos também passaram. A integração foi verificada no serviço MySQL do Actions, não nesse ambiente local.

A inspeção de `aplicacao.url_map` confirmou 21 regras (20 da aplicação e arquivos estáticos). O protótipo inicial teve sintaxe e abertura/saída do menu verificadas.

A [execução 35215464669](https://github.com/gustavonm20/Sistema-de-comandas/actions/runs/35215464669), no registro de alteração `21aa781e5638216125c767350befe12a2ed0e813`, confirmou novamente os testes e verificou a documentação publicada: 138 ligações locais/imagens em 22 arquivos Markdown.

## Executar sem MySQL

Na raiz, com as dependências instaladas:

```powershell
python -m unittest discover -s testes -p 'teste_*.py' -v
python ferramentas/verificar_documentacao.py
```

Sem `EXECUTAR_TESTES_MYSQL=1`, a saída informa `skipped` para os testes do banco. Não confundir essa execução com validação de persistência. `verificar_documentacao.py` verifica destinos locais, imagens e âncoras de arquivos Markdown versionados; não acessa ligações externos nem valida o significado dos textos.

## Executar integração real

Use um banco **descartável** cujo nome comece por `fluxopag_teste_`. A suíte apaga registros das tabelas de negócio em cada teste. Nunca use o banco de trabalho.

Em outro terminal PowerShell, configure o ambiente de teste; esses valores prevalecem sobre `.env`:

```powershell
$env:MYSQL_BANCO = "fluxopag_teste_local"
$env:MYSQL_USUARIO = "root"
$env:MYSQL_SENHA = Read-Host "Senha do MySQL local" -MaskInput
$env:EXECUTAR_TESTES_MYSQL = "1"
python inicializar_banco.py
python -m unittest discover -s testes -p 'teste_*.py' -v
Remove-Item Env:EXECUTAR_TESTES_MYSQL, Env:MYSQL_BANCO, Env:MYSQL_USUARIO, Env:MYSQL_SENHA
```

`-MaskInput` exige PowerShell 7.1+. No Windows PowerShell 5.1, use um usuário de teste e configure a senha em um `.env` local temporário ignorado pelo Git; não a inclua no histórico do terminal. Outra opção é executar a mesma suíte pela rotina. Se o banco de testes já estiver inicializado, pule o inicializador: a suíte faz a limpeza controlada. O prefixo é verificado antes de qualquer `DELETE`.

No Linux/macOS, exporte as mesmas variáveis e use `read -rs MYSQL_SENHA; export MYSQL_SENHA` para não exibir a senha. Mantenha Python e MySQL no mesmo fuso; a integração contínua configura `America/Sao_Paulo` para ambos.

Para o histórico:

```powershell
cd legado/terminal-json
python -m unittest discover -p "teste_*.py" -v
```

## integração contínua e verificações ainda pendentes

[verificar.yml](../.github/workflows/verificar.yml) instala as três dependências, sobe MySQL, inicializa banco isolado e executa aplicação, legado e ligações. Usa `unittest`, já presente nos artefatos; não exige adotar Pytest apenas por constar de um plano antigo. A rotina não configura proteção do ramo: tornar verificações obrigatórios é uma configuração administrativa separada.

Ainda faltam: conexões concorrentes (#21, #14), migrações com dados antigos (#19), autenticação/CSRF (#24), acessibilidade e navegação real em computador/tablet (#16), revisão da instalação no Windows, testes completos dos filtros/POSTs HTTP e cenários de períodos sem dados/virada de ano (#15, #17). Não existe percentual de cobertura medido nem medição de desempenho publicado.
