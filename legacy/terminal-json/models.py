from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Product:
    product_id: int
    name: str
    price_cents: int
    category: str
    active: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Product":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OrderItem:
    product_id: int
    product_name: str
    unit_price_cents: int
    quantity: int

    @property
    def subtotal_cents(self) -> int:
        return self.unit_price_cents * self.quantity

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrderItem":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Order:
    order_number: int
    opened_at: str
    items: list[OrderItem] = field(default_factory=list)

    @property
    def total_cents(self) -> int:
        return sum(item.subtotal_cents for item in self.items)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Order":
        return cls(
            order_number=data["order_number"],
            opened_at=data["opened_at"],
            items=[OrderItem.from_dict(item) for item in data.get("items", [])],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "order_number": self.order_number,
            "opened_at": self.opened_at,
            "items": [item.to_dict() for item in self.items],
        }


@dataclass
class Sale:
    sale_id: int
    order_number: int
    items: list[OrderItem]
    total_cents: int
    payment_method: str
    closed_at: str
    cash_session_id: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Sale":
        return cls(
            sale_id=data["sale_id"],
            order_number=data["order_number"],
            items=[OrderItem.from_dict(item) for item in data.get("items", [])],
            total_cents=data["total_cents"],
            payment_method=data["payment_method"],
            closed_at=data["closed_at"],
            cash_session_id=data["cash_session_id"],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sale_id": self.sale_id,
            "order_number": self.order_number,
            "items": [item.to_dict() for item in self.items],
            "total_cents": self.total_cents,
            "payment_method": self.payment_method,
            "closed_at": self.closed_at,
            "cash_session_id": self.cash_session_id,
        }


@dataclass
class CashSession:
    session_id: int
    opened_at: str
    opening_balance_cents: int
    closed_at: str | None = None
    expected_cash_cents: int | None = None
    actual_cash_cents: int | None = None
    difference_cents: int | None = None

    @property
    def is_open(self) -> bool:
        return self.closed_at is None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CashSession":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
