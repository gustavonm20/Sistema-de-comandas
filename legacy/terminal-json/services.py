from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

from models import CashSession, Order, OrderItem, Product, Sale, now_iso
from storage import JsonStorage


class BusinessError(Exception):
    pass


class CommandService:
    MAX_ORDERS = 20
    PAYMENT_METHODS = {"1": "Dinheiro", "2": "Pix", "3": "Crédito", "4": "Débito"}

    def __init__(self, data_file: Path) -> None:
        self.storage = JsonStorage(data_file)
        self.products: list[Product] = []
        self.orders: list[Order] = []
        self.sales: list[Sale] = []
        self.cash_sessions: list[CashSession] = []
        self.reload()

    def reload(self) -> None:
        data = self.storage.load()
        self.products = [Product.from_dict(item) for item in data["products"]]
        self.orders = [Order.from_dict(item) for item in data["open_orders"]]
        self.sales = [Sale.from_dict(item) for item in data["sales"]]
        self.cash_sessions = [CashSession.from_dict(item) for item in data["cash_sessions"]]

    def save(self) -> None:
        self.storage.save({
            "products": [item.to_dict() for item in self.products],
            "open_orders": [item.to_dict() for item in self.orders],
            "sales": [item.to_dict() for item in self.sales],
            "cash_sessions": [item.to_dict() for item in self.cash_sessions],
        })

    @property
    def current_cash_session(self) -> CashSession | None:
        return next((session for session in reversed(self.cash_sessions) if session.is_open), None)

    def add_product(self, name: str, price_cents: int, category: str) -> Product:
        if not name.strip() or not category.strip():
            raise BusinessError("Nome e categoria são obrigatórios.")
        if price_cents <= 0:
            raise BusinessError("O preço deve ser maior que zero.")
        product = Product(self._next_id(self.products, "product_id"), name.strip(), price_cents, category.strip())
        self.products.append(product)
        self.save()
        return product

    def find_product(self, product_id: int, require_active: bool = False) -> Product:
        product = next((item for item in self.products if item.product_id == product_id), None)
        if product is None:
            raise BusinessError("Produto não encontrado.")
        if require_active and not product.active:
            raise BusinessError("Este produto está desativado.")
        return product

    def search_products(self, term: str) -> list[Product]:
        normalized = term.strip().casefold()
        return [item for item in self.products if normalized in item.name.casefold() or normalized in item.category.casefold()]

    def edit_product(self, product_id: int, name: str, price_cents: int, category: str) -> Product:
        product = self.find_product(product_id)
        if not name.strip() or not category.strip() or price_cents <= 0:
            raise BusinessError("Informe nome, preço e categoria válidos.")
        product.name = name.strip()
        product.price_cents = price_cents
        product.category = category.strip()
        self.save()
        return product

    def deactivate_product(self, product_id: int) -> None:
        product = self.find_product(product_id)
        if not product.active:
            raise BusinessError("O produto já está desativado.")
        product.active = False
        self.save()

    def open_cash(self, opening_balance_cents: int) -> CashSession:
        if self.current_cash_session:
            raise BusinessError("O dia já foi iniciado.")
        if opening_balance_cents < 0:
            raise BusinessError("O saldo inicial não pode ser negativo.")
        session = CashSession(self._next_id(self.cash_sessions, "session_id"), now_iso(), opening_balance_cents)
        self.cash_sessions.append(session)
        self.save()
        return session

    def close_cash(self, actual_cash_cents: int) -> CashSession:
        session = self.current_cash_session
        if session is None:
            raise BusinessError("Não existe um dia aberto.")
        if self.orders:
            numbers = ", ".join(str(order.order_number) for order in self.orders)
            raise BusinessError(f"Fechamento bloqueado. Comandas abertas: {numbers}.")
        if actual_cash_cents < 0:
            raise BusinessError("O valor contado não pode ser negativo.")
        cash_sales = sum(
            sale.total_cents for sale in self.sales
            if sale.cash_session_id == session.session_id and sale.payment_method == "Dinheiro"
        )
        expected = session.opening_balance_cents + cash_sales
        session.closed_at = now_iso()
        session.expected_cash_cents = expected
        session.actual_cash_cents = actual_cash_cents
        session.difference_cents = actual_cash_cents - expected
        self.save()
        return session

    def open_order(self, order_number: int) -> Order:
        if self.current_cash_session is None:
            raise BusinessError("Inicie o dia antes de abrir comandas.")
        self._validate_order_number(order_number)
        if any(item.order_number == order_number for item in self.orders):
            raise BusinessError("Esta comanda já está aberta.")
        order = Order(order_number, now_iso())
        self.orders.append(order)
        self.save()
        return order

    def find_order(self, order_number: int) -> Order:
        order = next((item for item in self.orders if item.order_number == order_number), None)
        if order is None:
            raise BusinessError("Comanda não está aberta.")
        return order

    def add_item(self, order_number: int, product_id: int, quantity: int) -> None:
        if quantity <= 0:
            raise BusinessError("A quantidade deve ser maior que zero.")
        order = self.find_order(order_number)
        product = self.find_product(product_id, require_active=True)
        existing = next((item for item in order.items if item.product_id == product_id), None)
        if existing:
            existing.quantity += quantity
        else:
            order.items.append(OrderItem(product.product_id, product.name, product.price_cents, quantity))
        self.save()

    def remove_item(self, order_number: int, product_id: int, quantity: int) -> None:
        if quantity <= 0:
            raise BusinessError("A quantidade deve ser maior que zero.")
        order = self.find_order(order_number)
        item = next((item for item in order.items if item.product_id == product_id), None)
        if item is None:
            raise BusinessError("Produto não está nesta comanda.")
        if quantity > item.quantity:
            raise BusinessError("A quantidade informada é maior que a registrada.")
        item.quantity -= quantity
        if item.quantity == 0:
            order.items.remove(item)
        self.save()

    def close_order(self, order_number: int, payment_option: str) -> Sale:
        session = self.current_cash_session
        if session is None:
            raise BusinessError("Não existe um dia aberto.")
        order = self.find_order(order_number)
        if not order.items:
            raise BusinessError("Não é possível fechar uma comanda vazia.")
        payment_method = self.PAYMENT_METHODS.get(payment_option)
        if payment_method is None:
            raise BusinessError("Forma de pagamento inválida.")
        sale = Sale(
            sale_id=self._next_id(self.sales, "sale_id"),
            order_number=order.order_number,
            items=order.items.copy(),
            total_cents=order.total_cents,
            payment_method=payment_method,
            closed_at=now_iso(),
            cash_session_id=session.session_id,
        )
        self.sales.append(sale)
        self.orders.remove(order)
        self.save()
        return sale

    def period_summary(self, period: str, reference: date | None = None) -> dict[str, object]:
        reference = reference or date.today()
        start, end, previous_start, previous_end = self._period_bounds(period, reference)
        current_sales = self._sales_between(start, end)
        previous_sales = self._sales_between(previous_start, previous_end)
        total = sum(item.total_cents for item in current_sales)
        previous_total = sum(item.total_cents for item in previous_sales)
        change = None if previous_total == 0 else ((total - previous_total) / previous_total) * 100
        payments: dict[str, int] = {}
        products: dict[str, int] = {}
        for sale in current_sales:
            payments[sale.payment_method] = payments.get(sale.payment_method, 0) + sale.total_cents
            for item in sale.items:
                products[item.product_name] = products.get(item.product_name, 0) + item.quantity
        top_products = sorted(products.items(), key=lambda item: (-item[1], item[0]))[:5]
        return {
            "start": start,
            "end": end,
            "sales_count": len(current_sales),
            "total_cents": total,
            "average_cents": total // len(current_sales) if current_sales else 0,
            "payments": payments,
            "top_products": top_products,
            "previous_total_cents": previous_total,
            "change_percent": change,
        }

    def _sales_between(self, start: date, end: date) -> list[Sale]:
        return [sale for sale in self.sales if start <= datetime.fromisoformat(sale.closed_at).date() <= end]

    @staticmethod
    def _period_bounds(period: str, reference: date) -> tuple[date, date, date, date]:
        if period == "day":
            return reference, reference, reference - timedelta(days=1), reference - timedelta(days=1)
        if period == "week":
            start = reference - timedelta(days=reference.weekday())
            end = start + timedelta(days=6)
            return start, end, start - timedelta(days=7), end - timedelta(days=7)
        if period == "month":
            start = reference.replace(day=1)
            next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
            end = next_month - timedelta(days=1)
            previous_end = start - timedelta(days=1)
            previous_start = previous_end.replace(day=1)
            return start, end, previous_start, previous_end
        raise BusinessError("Período inválido.")

    @staticmethod
    def _next_id(items: list[object], attribute: str) -> int:
        return max((getattr(item, attribute) for item in items), default=0) + 1

    def _validate_order_number(self, order_number: int) -> None:
        if not 1 <= order_number <= self.MAX_ORDERS:
            raise BusinessError(f"A comanda deve estar entre 1 e {self.MAX_ORDERS}.")
