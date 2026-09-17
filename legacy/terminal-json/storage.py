from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class JsonStorage:
    DEFAULT_DATA: dict[str, Any] = {
        "products": [],
        "open_orders": [],
        "sales": [],
        "cash_sessions": [],
    }

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict[str, Any]:
        if not self.file_path.exists():
            self.save(self.DEFAULT_DATA.copy())
            return self.DEFAULT_DATA.copy()

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError) as error:
            raise RuntimeError(
                "Não foi possível ler o banco de dados. "
                "Verifique o arquivo data/database.json."
            ) from error

        for key, default_value in self.DEFAULT_DATA.items():
            data.setdefault(key, default_value.copy())
        return data

    def save(self, data: dict[str, Any]) -> None:
        temporary_file = self.file_path.with_suffix(".tmp")
        try:
            with temporary_file.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
                file.flush()
                os.fsync(file.fileno())
            temporary_file.replace(self.file_path)
        except OSError as error:
            raise RuntimeError("Não foi possível salvar os dados.") from error
