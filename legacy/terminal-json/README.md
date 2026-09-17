# FluxoPag — evolução histórica do terminal

[Voltar ao projeto](../../README.md) · [Origem](../../docs/PROVENANCE.md)

Código recuperado de `FluxoPag_Prototipo_Final.zip`, preservado como etapa de aprendizado. A persistência é um arquivo JSON local; esta pasta não é o backend da aplicação Flask nem uma alternativa de banco para a versão MySQL.

Os módulos exploram produtos, vinte comandas, itens, pagamento registrado, histórico, operação diária, conferência de caixa e consultas de resumos no terminal. Os seis testes existentes passaram na revisão de 17/09/2026; isso não comprova todos os caminhos interativos nem garante equivalência com as regras da web. A numeração interna usa inteiros, diferentemente do `CHAR(4)` da aplicação atual.

Com Python 3.10+, dentro desta pasta:

```powershell
python main.py
python -m unittest discover -p "test_*.py" -v
```

No Windows, `py main.py` também pode ser usado. Não são necessárias dependências externas. `data/database.json` é criado localmente e ignorado pelo Git. Use dados fictícios; não há importação desse arquivo para MySQL nem migração automática para a web.
