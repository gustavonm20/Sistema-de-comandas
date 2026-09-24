# Instalação e execução

[Índice](README.md) · [Banco](BANCO_DADOS.md) · [Verificação](TESTES.md)

## Requisitos

- Python 3.10 ou superior; a integração contínua usa Python 3.12.
- MySQL Servidor 8.0.16+ (necessário para aplicar `CHECK`), preferencialmente 8.4, e um usuário autorizado a criar a estrutura inicial.
- Git. MySQL Workbench é opcional; ele não substitui o servidor.

A versão web está na ramo principal `main`, com os fontes e a configuração descritos neste guia. Não existe implantação desta versão documentada como produção. Execute em `127.0.0.1`: autenticação e proteção CSRF ainda estão na [tarefa #24](https://github.com/gustavonm20/Sistema-de-comandas/issues/24).

## Preparar o projeto no Windows

No PowerShell:

```powershell
git clone https://github.com/gustavonm20/Sistema-de-comandas.git
cd Sistema-de-comandas
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r dependencias.txt
Copy-Item .env.exemplo .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Se o PowerShell bloquear a ativação, use diretamente `.\.venv\Scripts\python.exe` no lugar de `python` nos comandos. Não é necessário alterar a política de execução do computador.

No Linux/macOS, substitua a criação e ativação por:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r dependencias.txt
cp .env.exemplo .env
```

## Configurar credenciais locais

Edite `.env` na raiz. O arquivo [`.env.exemplo`](../.env.exemplo) corresponde às variáveis usadas por [aplicacao.py](../aplicacao.py).

| Variável | Valor de exemplo / função |
| --- | --- |
| `MYSQL_SERVIDOR` | `127.0.0.1`, endereço do servidor |
| `MYSQL_PORTA` | `3306` |
| `MYSQL_BANCO` | `comandas`; banco novo ou vazio |
| `MYSQL_USUARIO` | `fluxopag`, usuário da aplicação |
| `MYSQL_SENHA` | Senha local desse usuário; não publicar |
| `FLASK_CHAVE_SECRETA` | Resultado do comando `secrets.token_hex(32)` acima |

`python-dotenv` lê o arquivo ao lado de `aplicacao.py`, independentemente do diretório atual; variáveis já definidas no ambiente têm precedência. Sem chave, o processo gera uma chave temporária e as sessões deixam de valer após reiniciar. Sem configuração, o código herdado assume usuário `root`; use o usuário restrito do exemplo no trabalho diário.

## Inicializar um banco vazio

Confirme que o MySQL está rodando. Com as configurações do servidor no `.env`, execute:

```powershell
python inicializar_banco.py --usuario root --solicitar-senha
```

Esse comando solicita a senha administrativa sem gravá-la no projeto, cria o banco indicado em `MYSQL_BANCO`, nove tabelas, sete visões, categorias, vinte cartões de `0001` a `0020` e um estabelecimento fictício. Ele **recusa qualquer banco que já contenha tabelas**. Não apaga dados nem transforma uma estrutura antiga. Uma falha no meio da inicialização pode deixar tabelas criadas, pois DDL do MySQL faz confirmação implícita; investigue a causa antes de tentar novamente.

No cliente MySQL ou Workbench, conectado como administrador, crie o usuário local da aplicação. Substitua a senha ilustrativa e ajuste o nome do banco se tiver escolhido outro:

```sql
CREATE USER 'fluxopag'@'localhost' IDENTIFIED BY 'SUBSTITUA_POR_UMA_SENHA_LOCAL';
GRANT SELECT, INSERT, UPDATE, DELETE ON comandas.* TO 'fluxopag'@'localhost';
```

Se o usuário já existe, confira suas permissões; não recrie nem redefina sua senha sem necessidade. A identificação do host depende da configuração MySQL: confirme que o usuário autorizado corresponde à conexão local feita pela aplicação.

Alternativamente, o administrador pode executar [banco_dados/estrutura.sql](../banco_dados/estrutura.sql) inteiro no Workbench **apenas em banco novo**. Esse arquivo fixa `comandas`; o inicializador Python é a opção que respeita outro `MYSQL_BANCO`. `CREATE TABLE IF NOT EXISTS` não acrescenta colunas a instalações antigas. Consulte a [compatibilidade](BANCO_DADOS.md#compatibilidade-e-evolução).

O [conjunto de dados demonstrativos](../banco_dados/dados_exemplo.sql) é opcional e contém três produtos fictícios. Execute-o na estrutura recém-criado pelo Workbench. Não contém vendas nem informações de clientes.

## Iniciar a aplicação web

```powershell
python aplicacao.py
```

Abra `http://127.0.0.1:5000`. Cadastre produtos, acesse **Conta e operação** para informar o saldo inicial, abra uma comanda disponível e inclua itens. Ao registrar o pagamento, a venda passa ao histórico e o número fica disponível. Ao encerrar a operação, informe o dinheiro contado; havendo diferença, registre justificativa de pelo menos cinco caracteres. `Ctrl+C` encerra o servidor de desenvolvimento.

Os resumos são páginas distintas por período: `/resumos?periodo=diario`, `semanal` e `mensal`. Eles usam datas de calendário, não uma operação encerrada selecionada. O [guia de regras](REGRAS_NEGOCIO.md) explica essa diferença.

## Executar os protótipos históricos

O treino inicial usa memória e não exige Flask nem banco:

```powershell
python "protótipo-inicial.py"
```

A evolução JSON tem outro ponto de entrada:

```powershell
cd legado/terminal-json
python principal.py
python -m unittest discover -p "teste_*.py" -v
```

Os arquivos JSON locais dessa versão não alimentam o MySQL. Não há importador entre os protótipos.

## Problemas frequentes

| Sintoma | Verificação prática |
| --- | --- |
| `ModuleNotFoundError` | Instale `dependencias.txt` com o mesmo Python usado para iniciar o projeto. |
| Página de banco indisponível (503) | Confira serviço MySQL, servidor, porta, senha, banco e permissões. Detalhes ficam no registro local, não no HTML. |
| Tabela ou coluna ausente | A aplicação recebeu uma estrutura antiga. Preserve o banco e siga a conversão de dados documentada. Estruturas mais antigas continuam na tarefa #19. |
| Inicializador recusa o banco | Comportamento esperado se houver tabelas; ele não é uma ferramenta de atualização. |
| Acesso negado pelo MySQL | Confira usuário, servidor associado e privilégios. Não coloque a senha no comando ou no Git. |
| Formulários perdem mensagens após reiniciar | Configure uma `FLASK_CHAVE_SECRETA` estável no `.env`. |
| Não é possível abrir comanda | Inicie a operação e selecione um cartão ativo e livre. |
| Não é possível encerrar o dia | Conclua as comandas abertas; uma comanda vazia ainda não possui fluxo de cancelamento. Veja #12. |
| Datas divergentes | Python e MySQL devem usar o mesmo fuso local. `DATETIME` não armazena fuso; não há configuração por estabelecimento. |

Para testar, siga [TESTES.md](TESTES.md). O banco da suíte de integração é descartável e deve ter prefixo `fluxopag_teste_`.

## Atualizar uma instalação existente

Esta tradução mudou nomes de arquivos, campos e variáveis de configuração. Use `aplicacao.py` e `dependencias.txt` após atualizar o repositório; copie suas credenciais locais para os nomes de [.env.exemplo](../.env.exemplo). Não publique o `.env`.

Se já tem dados na versão Flask com tabelas em inglês, siga a [conversão do banco](BANCO_DADOS.md#compatibilidade-e-evolução). Ela cria o destino sozinha e mantém a origem. Não inicialize o destino antes de copiar. O VS Code continua sendo o editor; é necessário manter o servidor MySQL em execução.
