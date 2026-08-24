# FluxoPag — Sistema de Comandas

O **FluxoPag** é um sistema de comandas pensado para padarias, cafeterias e pequenos estabelecimentos. O objetivo é centralizar produtos, comandas, pagamentos, histórico de vendas, abertura e fechamento do dia e resumos gerenciais.

> O projeto está em fase de evolução da prototipação para a fundação técnica. O protótipo didático em Python continua como material de treino, enquanto o banco MySQL começa a representar a estrutura da futura aplicação alinhada ao Figma.

## Estado atual

| Área | Situação |
| --- | --- |
| Protótipo de terminal em Python | Funcional para treino e evolução da lógica |
| Protótipo hi-fi no Figma | Em desenvolvimento |
| Fluxos de navegação no Figma | Parcialmente conectados |
| Low-fi das telas | Em desenvolvimento |
| Modelagem MySQL | Em andamento |
| Schema MySQL inicial | Implementado |
| Views de produtos, comandas, histórico e resumos | Implementadas |
| Aplicação web | Planejada |
| Testes e deploy | Planejados |

## Protótipo no Figma

O protótipo atual contempla:

- dashboard;
- produtos;
- listagem de comandas;
- detalhes de uma comanda;
- criação de nova comanda;
- pagamento e confirmação;
- histórico de vendas;
- conta do estabelecimento;
- estado de dia não iniciado;
- estado de dia em andamento;
- ação de iniciar e finalizar o dia;
- resumos do dia, da semana e do mês;
- parte dos wireframes low-fi;
- conexões principais de navegação.

[Acessar o protótipo no Figma](https://www.figma.com/design/Rau8PgbGwiiJwRo9MHgzMW/Comandas?node-id=0-1)

## Regras de negócio principais

- A conta autenticada representa o **estabelecimento**, não um funcionário específico no primeiro MVP.
- Cada comanda é identificada por um número fixo e reutilizável.
- A comanda não exige o nome do cliente.
- O número da comanda possui quatro dígitos no banco.
- Uma mesma comanda física não pode possuir dois atendimentos abertos simultaneamente.
- Ao ser fechada, a comanda fica disponível para um novo atendimento.
- Produtos desativados permanecem registrados para preservar o histórico.
- O preço consumido é armazenado no item da comanda para que mudanças futuras no catálogo não alterem vendas antigas.
- O estabelecimento deve iniciar o dia antes de contabilizar vendas e comandas no fluxo final.
- O dia não poderá ser finalizado enquanto existirem comandas abertas.
- Os dados finalizados alimentam os resumos diário, semanal e mensal.

Mais detalhes estão em [docs/BUSINESS_RULES.md](docs/BUSINESS_RULES.md).

## Banco de dados

O banco oficial em desenvolvimento utiliza **MySQL 8** e pode ser executado pelo MySQL Workbench.

O schema atual possui:

- `categories`;
- `products`;
- `command_cards`;
- `orders`;
- `order_items`;
- `sales`;
- views para produtos, comandas abertas, resumo da comanda, histórico e indicadores por período.

Arquivos:

- [Schema MySQL](database/schema.sql)
- [Documentação do banco](docs/DATABASE.md)

## Tecnologias

### Protótipo de treino

- Python 3
- Execução em terminal
- Estruturas em memória

### Fundação técnica atual

- MySQL 8
- MySQL Workbench
- SQL relacional com constraints, views, window functions e índices

### Aplicação web planejada

- Python no backend
- integração com MySQL
- frontend baseado no protótipo do Figma
- Pytest
- GitHub Actions

A escolha definitiva do framework web será registrada quando a estrutura da aplicação for iniciada; a documentação antiga que fixava Flask + SQLite foi substituída pela decisão atual de utilizar MySQL.

## Executando o protótipo de terminal

```bash
git clone https://github.com/gustavonm20/Sistema-de-comandas.git
cd Sistema-de-comandas
python app.py
```

## Executando o banco

Abra `database/schema.sql` no MySQL Workbench e execute o script completo.

Para conferir as tabelas e views:

```sql
SHOW FULL TABLES;
```

## Organização do repositório

```text
Sistema-de-comandas/
├── app.py
├── database/
│   └── schema.sql
├── README.md
├── ROADMAP.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── docs/
│   ├── BUSINESS_RULES.md
│   ├── DATABASE.md
│   ├── FIGMA_STATUS.md
│   └── KANBAN.md
└── .github/
```

## Planejamento

- [Quadro Kanban do projeto](https://github.com/users/gustavonm20/projects/2/views/4)
- [Roadmap](ROADMAP.md)
- [Organização do Kanban](docs/KANBAN.md)
- [Banco de dados](docs/DATABASE.md)
- [Situação do Figma](docs/FIGMA_STATUS.md)
- [Regras de negócio](docs/BUSINESS_RULES.md)
- [Issues](https://github.com/gustavonm20/Sistema-de-comandas/issues)

## Contribuição

As orientações de branches, commits, issues e pull requests estão em [CONTRIBUTING.md](CONTRIBUTING.md).
