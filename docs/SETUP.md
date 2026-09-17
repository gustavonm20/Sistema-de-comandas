# Instalação e execução

[Índice](README.md) · [Banco](DATABASE.md) · [Verificação](TESTING.md)

## Requisitos

- Python 3.10 ou superior; a CI usa Python 3.12.
- MySQL Server 8.0.16+ (necessário para aplicar `CHECK`), preferencialmente 8.4, e um usuário autorizado a criar a estrutura inicial.
- Git. MySQL Workbench é opcional; ele não substitui o servidor.

A versão web está na branch `chore/consolidar-fluxopag`, proposta para revisão. Não existe implantação desta versão documentada como produção. Execute em `127.0.0.1`: autenticação e proteção CSRF ainda estão na [issue #24](https://github.com/gustavonm20/Sistema-de-comandas/issues/24).

## Preparar o projeto no Windows

No PowerShell:

```powershell
git clone https://github.com/gustavonm20/Sistema-de-comandas.git
cd Sistema-de-comandas
git switch chore/consolidar-fluxopag
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Se o PowerShell bloquear a ativação, use diretamente `.\.venv\Scripts\python.exe` no lugar de `python` nos comandos. Não é necessário alterar a política de execução do computador.

No Linux/macOS, substitua a criação e ativação por:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

## Configurar credenciais locais

Edite `.env` na raiz. O arquivo [`.env.example`](../.env.example) corresponde às variáveis usadas por [app.py](../app.py).

| Variável | Valor de exemplo / função |
| --- | --- |
| `MYSQL_HOST` | `127.0.0.1`, endereço do servidor |
| `MYSQL_PORT` | `3306` |
| `MYSQL_DATABASE` | `comandas_db`; banco novo ou vazio |
| `MYSQL_USER` | `fluxopag`, usuário da aplicação |
| `MYSQL_PASSWORD` | Senha local desse usuário; não publicar |
| `FLASK_SECRET_KEY` | Resultado do comando `secrets.token_hex(32)` acima |

`python-dotenv` lê o arquivo ao lado de `app.py`, independentemente do diretório atual; variáveis já definidas no ambiente têm precedência. Sem chave, o processo gera uma chave temporária e as sessões deixam de valer após reiniciar. Sem configuração, o código herdado assume usuário `root`; use o usuário restrito do exemplo no trabalho diário.

## Inicializar um banco vazio

Confirme que o MySQL está rodando. Com as configurações do servidor no `.env`, execute:

```powershell
python initialize_database.py --user root --ask-password
```

Esse comando solicita a senha administrativa sem gravá-la no projeto, cria o banco indicado em `MYSQL_DATABASE`, nove tabelas, sete views, categorias, vinte cartões de `0001` a `0020` e um estabelecimento fictício. Ele **recusa qualquer banco que já contenha tabelas**. Não apaga dados nem transforma um schema antigo. Uma falha no meio da inicialização pode deixar tabelas criadas, pois DDL do MySQL faz commit; investigue a causa antes de tentar novamente.

No cliente MySQL ou Workbench, conectado como administrador, crie o usuário local da aplicação. Substitua a senha ilustrativa e ajuste o nome do banco se tiver escolhido outro:

```sql
CREATE USER 'fluxopag'@'localhost' IDENTIFIED BY 'SUBSTITUA_POR_UMA_SENHA_LOCAL';
GRANT SELECT, INSERT, UPDATE, DELETE ON comandas_db.* TO 'fluxopag'@'localhost';
```

Se o usuário já existe, confira suas permissões; não recrie nem redefina sua senha sem necessidade. A identificação do host depende da configuração MySQL: confirme que o usuário autorizado corresponde à conexão local feita pela aplicação.

Alternativamente, o administrador pode executar [database/schema.sql](../database/schema.sql) inteiro no Workbench **apenas em banco novo**. Esse arquivo fixa `comandas_db`; o inicializador Python é a opção que respeita outro `MYSQL_DATABASE`. `CREATE TABLE IF NOT EXISTS` não acrescenta colunas a instalações antigas. Consulte a [compatibilidade](DATABASE.md#compatibilidade-e-evolução).

O [seed demonstrativo](../database/demo_seed.sql) é opcional e contém três produtos fictícios. Execute-o no schema recém-criado pelo Workbench. Não contém vendas nem informações de clientes.

## Iniciar a aplicação web

```powershell
python app.py
```

Abra `http://127.0.0.1:5000`. Cadastre produtos, acesse **Conta e operação** para informar o saldo inicial, abra uma comanda disponível e inclua itens. Ao registrar o pagamento, a venda passa ao histórico e o número fica disponível. Ao encerrar a operação, informe o dinheiro contado; havendo diferença, registre justificativa de pelo menos cinco caracteres. `Ctrl+C` encerra o servidor de desenvolvimento.

Os resumos são páginas distintas por período: `/reports?period=daily`, `weekly` e `monthly`. Eles usam datas de calendário, não uma operação encerrada selecionada. O [guia de regras](BUSINESS_RULES.md) explica essa diferença.

## Executar os protótipos históricos

O treino inicial usa memória e não exige Flask nem banco:

```powershell
python "protótipo-inicial.py"
```

A evolução JSON tem outro ponto de entrada:

```powershell
cd legacy/terminal-json
python main.py
python -m unittest discover -p "test_*.py" -v
```

Os arquivos JSON locais dessa versão não alimentam o MySQL. Não há importador entre os protótipos.

## Problemas frequentes

| Sintoma | Verificação prática |
| --- | --- |
| `ModuleNotFoundError` | Instale `requirements.txt` com o mesmo Python usado para iniciar o projeto. |
| Página de banco indisponível (503) | Confira serviço MySQL, host, porta, senha, banco e permissões. Detalhes ficam no log local, não no HTML. |
| Tabela ou coluna ausente | A aplicação recebeu um schema antigo. Preserve-o; inicialize outro banco vazio para experimentar esta branch. Migration está na #19. |
| Inicializador recusa o banco | Comportamento esperado se houver tabelas; ele não é uma ferramenta de atualização. |
| Acesso negado pelo MySQL | Confira usuário, host associado e privilégios. Não coloque a senha no comando ou no Git. |
| Formulários perdem mensagens após reiniciar | Configure uma `FLASK_SECRET_KEY` estável no `.env`. |
| Não é possível abrir comanda | Inicie a operação e selecione um cartão ativo e livre. |
| Não é possível encerrar o dia | Conclua as comandas abertas; uma comanda vazia ainda não possui fluxo de cancelamento. Veja #12. |
| Datas divergentes | Python e MySQL devem usar o mesmo fuso local. `DATETIME` não armazena fuso; não há configuração por estabelecimento. |

Para testar, siga [TESTING.md](TESTING.md). O banco da suíte de integração é descartável e deve ter prefixo `fluxopag_test_`.
