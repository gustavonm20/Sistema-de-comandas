# FluxoPag — Sistema de Comandas

O **FluxoPag** é um sistema de comandas pensado para padarias, cafeterias e pequenos estabelecimentos. O objetivo é centralizar produtos, comandas, pagamentos, histórico de vendas, abertura e fechamento do dia e resumos gerenciais.

> O projeto está em fase de **prototipação e definição das regras de negócio**. O código atual em Python é um protótipo didático de terminal; a aplicação web ainda será desenvolvida.

## Estado atual

| Área | Situação |
| --- | --- |
| Protótipo de terminal em Python | Em desenvolvimento |
| Protótipo hi-fi no Figma | Em desenvolvimento |
| Fluxos de navegação no Figma | Parcialmente conectados |
| Low-fi das telas | Em desenvolvimento |
| Aplicação web com Flask e SQLite | Planejada |
| Testes e deploy | Planejados |

## Protótipo no Figma

O protótipo atual já contempla:

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

### Próximas melhorias de design

- confirmação antes de finalizar o dia;
- bloqueio do fechamento quando existirem comandas abertas;
- abertura de caixa com valor inicial;
- fechamento de caixa com valor esperado, valor contado e divergência;
- comparação entre dia, semana e mês atuais e anteriores;
- low-fi de todos os novos fluxos;
- revisão da ordem, nomes e alinhamento de todas as telas.

## Regras de negócio principais

- A conta autenticada representa o **estabelecimento**, não um funcionário específico.
- Cada comanda é identificada por um número fixo e reutilizável.
- A comanda não exige o nome do cliente.
- Ao ser fechada, a comanda fica disponível para um novo atendimento.
- O estabelecimento deve iniciar o dia antes de contabilizar vendas e comandas.
- O dia não poderá ser finalizado enquanto existirem comandas abertas.
- Ao finalizar o dia, os dados consolidados alimentam os resumos diário, semanal e mensal.
- O fechamento de caixa deve registrar divergências entre o valor esperado e o valor contado.

Mais detalhes estão em [docs/BUSINESS_RULES.md](docs/BUSINESS_RULES.md).

## Tecnologias

### Protótipo atual

- Python 3
- Execução em terminal
- Armazenamento temporário em memória

### Aplicação planejada

- Python
- Flask
- SQLite
- HTML, CSS e JavaScript
- Testes automatizados com Pytest
- GitHub Actions para integração contínua

## Executando o protótipo de terminal

```bash
git clone https://github.com/gustavonm20/Sistema-de-comandas.git
cd Sistema-de-comandas
python app.py
```

O arquivo `app.py` atualmente implementa parte do módulo de produtos. Os módulos de comandas, histórico e resumos ainda possuem etapas provisórias.

## Organização do repositório

```text
Sistema-de-comandas/
├── app.py
├── README.md
├── ROADMAP.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── docs/
│   ├── BUSINESS_RULES.md
│   ├── FIGMA_STATUS.md
│   └── KANBAN.md
└── .github/
    ├── ISSUE_TEMPLATE/
    │   └── feature_request.md
    └── pull_request_template.md
```

## Planejamento

- [Quadro Kanban do projeto](https://github.com/users/gustavonm20/projects/2/views/4)
- [Roadmap do projeto](ROADMAP.md)
- [Organização sugerida do Kanban](docs/KANBAN.md)
- [Situação do protótipo no Figma](docs/FIGMA_STATUS.md)
- [Regras de negócio](docs/BUSINESS_RULES.md)
- [Issues do projeto](https://github.com/gustavonm20/Sistema-de-comandas/issues)

## Acompanhamento rápido

O andamento do projeto deve ser acompanhado pelo Kanban e pelas issues. O `ROADMAP.md` apresenta a ordem geral das fases, enquanto cada issue contém escopo, dependências e critérios de aceitação.

## Contribuição

As orientações de branches, commits, issues e pull requests estão em [CONTRIBUTING.md](CONTRIBUTING.md).
