from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from compatibilidade import converter_dados_antigos


class ArmazenamentoJson:
    DADOS_INICIAIS: dict[str, Any] = {
        "produtos": [],
        "pedidos_abertos": [],
        "vendas": [],
        "sessoes_caixa": [],
    }

    def __init__(instancia, caminho_arquivo: Path) -> None:
        instancia.caminho_arquivo = caminho_arquivo
        instancia.caminho_arquivo.parent.mkdir(parents=True, exist_ok=True)

    def carregar(instancia) -> dict[str, Any]:
        origem = instancia.caminho_arquivo
        if not origem.exists():
            anterior = origem.parent.parent / "data" / "database.json"
            if anterior.is_file():
                origem = anterior
        if not origem.exists():
            instancia.salvar(instancia.DADOS_INICIAIS.copy())
            return instancia.DADOS_INICIAIS.copy()

        try:
            with origem.open("r", encoding="utf-8") as arquivo:
                dados = converter_dados_antigos(json.load(arquivo))
        except (json.JSONDecodeError, OSError) as erro:
            raise RuntimeError(
                "Não foi possível ler o banco de dados. "
                "Verifique o arquivo dados/banco.json."
            ) from erro

        for chave, valor_padrao in instancia.DADOS_INICIAIS.items():
            dados.setdefault(chave, valor_padrao.copy())
        return dados

    def salvar(instancia, dados: dict[str, Any]) -> None:
        arquivo_temporario = instancia.caminho_arquivo.with_suffix(".tmp")
        try:
            with arquivo_temporario.open("w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=2)
                arquivo.flush()
                os.fsync(arquivo.fileno())
            arquivo_temporario.replace(instancia.caminho_arquivo)
        except OSError as erro:
            raise RuntimeError("Não foi possível salvar os dados.") from erro
