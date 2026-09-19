from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Produto:
    id_produto: int
    nome: str
    preco_centavos: int
    categoria: str
    ativo: bool = True

    @classmethod
    def de_dicionario(classe, dados: dict[str, Any]) -> "Produto":
        return classe(**dados)

    def para_dicionario(instancia) -> dict[str, Any]:
        return asdict(instancia)


@dataclass
class ItemPedido:
    id_produto: int
    nome_produto: str
    preco_unitario_centavos: int
    quantidade: int

    @property
    def subtotal_centavos(instancia) -> int:
        return instancia.preco_unitario_centavos * instancia.quantidade

    @classmethod
    def de_dicionario(classe, dados: dict[str, Any]) -> "ItemPedido":
        return classe(**dados)

    def para_dicionario(instancia) -> dict[str, Any]:
        return asdict(instancia)


@dataclass
class Pedido:
    numero_comanda: int
    aberto_em: str
    itens: list[ItemPedido] = field(default_factory=list)

    @property
    def total_centavos(instancia) -> int:
        return sum(item.subtotal_centavos for item in instancia.itens)

    @classmethod
    def de_dicionario(classe, dados: dict[str, Any]) -> "Pedido":
        return classe(
            numero_comanda=dados["numero_comanda"],
            aberto_em=dados["aberto_em"],
            itens=[ItemPedido.de_dicionario(item) for item in dados.get("itens", [])],
        )

    def para_dicionario(instancia) -> dict[str, Any]:
        return {
            "numero_comanda": instancia.numero_comanda,
            "aberto_em": instancia.aberto_em,
            "itens": [item.para_dicionario() for item in instancia.itens],
        }


@dataclass
class Venda:
    id_venda: int
    numero_comanda: int
    itens: list[ItemPedido]
    total_centavos: int
    forma_pagamento: str
    fechado_em: str
    id_sessao_caixa: int

    @classmethod
    def de_dicionario(classe, dados: dict[str, Any]) -> "Venda":
        return classe(
            id_venda=dados["id_venda"],
            numero_comanda=dados["numero_comanda"],
            itens=[ItemPedido.de_dicionario(item) for item in dados.get("itens", [])],
            total_centavos=dados["total_centavos"],
            forma_pagamento=dados["forma_pagamento"],
            fechado_em=dados["fechado_em"],
            id_sessao_caixa=dados["id_sessao_caixa"],
        )

    def para_dicionario(instancia) -> dict[str, Any]:
        return {
            "id_venda": instancia.id_venda,
            "numero_comanda": instancia.numero_comanda,
            "itens": [item.para_dicionario() for item in instancia.itens],
            "total_centavos": instancia.total_centavos,
            "forma_pagamento": instancia.forma_pagamento,
            "fechado_em": instancia.fechado_em,
            "id_sessao_caixa": instancia.id_sessao_caixa,
        }


@dataclass
class SessaoCaixa:
    id_sessao: int
    aberto_em: str
    saldo_inicial_centavos: int
    fechado_em: str | None = None
    caixa_esperado_centavos: int | None = None
    caixa_contado_centavos: int | None = None
    diferenca_centavos: int | None = None

    @property
    def esta_aberto(instancia) -> bool:
        return instancia.fechado_em is None

    @classmethod
    def de_dicionario(classe, dados: dict[str, Any]) -> "SessaoCaixa":
        return classe(**dados)

    def para_dicionario(instancia) -> dict[str, Any]:
        return asdict(instancia)


def agora_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
