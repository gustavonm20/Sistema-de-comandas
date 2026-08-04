# Como contribuir

Este projeto usa issues e pull requests para manter o desenvolvimento organizado.

## Fluxo recomendado

1. Escolha uma issue aberta.
2. Leia o objetivo, as dependências e os critérios de aceitação.
3. Crie uma branch a partir da `main`.
4. Faça alterações pequenas e relacionadas a uma única tarefa.
5. Teste localmente.
6. Abra um pull request relacionando a issue.

## Padrão de branches

```text
feature/nome-da-funcionalidade
fix/nome-da-correcao
docs/nome-da-documentacao
test/nome-dos-testes
refactor/nome-da-refatoracao
```

Exemplos:

```text
feature/abrir-comanda
feature/fechamento-caixa
docs/modelagem-banco
fix/calculo-troco
```

## Padrão de commits

Use mensagens diretas no formato abaixo:

```text
tipo: descrição curta
```

Tipos recomendados:

- `feat`: nova funcionalidade;
- `fix`: correção de erro;
- `docs`: documentação;
- `test`: testes;
- `refactor`: melhoria interna sem alterar comportamento;
- `chore`: configuração e manutenção.

Exemplos:

```text
feat: adicionar abertura de comanda
fix: corrigir cálculo do troco
docs: atualizar regras de fechamento do caixa
test: validar bloqueio de comandas abertas
```

### Escopo de cada commit

- Cada commit deve representar uma alteração lógica e fácil de compreender.
- Evite agrupar arquivos sem relação apenas para reduzir a quantidade de commits.
- Documentação, configuração, testes e funcionalidades podem usar commits separados.
- A mensagem deve explicar o resultado da alteração, não apenas citar o nome do arquivo.
- O projeto deve permanecer executável sempre que possível após cada commit.

## Código

- Identificadores do código devem ser escritos em inglês.
- Textos exibidos ao usuário devem permanecer em português.
- Evite funções muito longas e responsabilidades misturadas.
- Valide entradas antes de alterar dados.
- Regras financeiras devem possuir testes.
- Não envie senhas, tokens ou arquivos `.env` ao repositório.

## Pull requests

Um pull request deve:

- possuir título claro;
- explicar o que foi alterado;
- citar a issue relacionada usando `Closes #número` quando aplicável;
- informar como a alteração foi testada;
- incluir screenshots quando houver mudança visual;
- manter o escopo restrito à tarefa proposta.

## Definition of Done

Uma tarefa pode ser considerada concluída quando:

- os critérios de aceitação da issue foram atendidos;
- o código executa sem erros conhecidos;
- os testes relevantes passam;
- a documentação foi atualizada quando necessário;
- a interface está consistente com o Figma, quando aplicável;
- o pull request foi integrado à `main`.
