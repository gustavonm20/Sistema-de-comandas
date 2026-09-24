# FluxoPag — evolução histórica do terminal

[Voltar ao projeto](../../README.md) · [Origem](../../documentacao/ORIGEM_ARQUIVOS.md)

Código recuperado de `FluxoPag_Prototipo_Final.zip`, preservado como etapa de aprendizado. A persistência é um arquivo JSON local; esta pasta não é o servidor da aplicação Flask nem uma alternativa de banco para a versão MySQL.

Os módulos exploram produtos, vinte comandas, itens, pagamento registrado, histórico, operação diária, conferência de caixa e consultas de resumos no terminal. Os seis testes existentes passaram na revisão de 17/09/2026; isso não comprova todos os caminhos interativos nem garante equivalência com as regras da web. A numeração interna usa inteiros, diferentemente do `CHAR(4)` da aplicação atual.

Com Python 3.10+, dentro desta pasta:

```powershell
python principal.py
python -m unittest discover -p "teste_*.py" -v
```

No Windows, `py principal.py` também pode ser usado. Não são necessárias dependências externas. `dados/banco.json` é criado localmente e ignorado pelo Git. Use dados fictícios; não há importação desse arquivo para MySQL nem migração automática para a web.

Os nomes próprios foram traduzidos em 19/09/2026. O carregador aceita as chaves antigas e, quando necessário, procura o arquivo anterior. Novas gravações vão para `dados/banco.json`; o arquivo antigo permanece intacto. O formato SQL e o formato JSON são independentes.
