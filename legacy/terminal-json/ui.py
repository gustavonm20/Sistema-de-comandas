from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path

from models import Order, Product, Sale
from services import BusinessError, CommandService


def format_cash(cents: int) -> str:
    value = cents / 100
    formatted = f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"


def parse_cash(text: str) -> int:
    normalized = text.strip().replace("R$", "").replace(" ", "")
    if not normalized:
        raise ValueError
    if "," in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    value = float(normalized)
    cents = round(value * 100)
    if value < 0:
        raise ValueError
    return cents


class TerminalApp:
    def __init__(self, data_file: Path) -> None:
        self.service = CommandService(data_file)

    def run(self) -> None:
        while True:
            self.clear()
            session_status = "ABERTO" if self.service.current_cash_session else "FECHADO"
            self.title(f"FLUXOPAG — SISTEMA DE COMANDAS | DIA {session_status}")
            print("1 - Produtos")
            print("2 - Comandas")
            print("3 - Histórico de vendas")
            print("4 - Resumo")
            print("5 - Caixa")
            print("0 - Encerrar sistema")
            match self.read_option():
                case 1: self.product_menu()
                case 2: self.order_menu()
                case 3: self.sales_history()
                case 4: self.summary_menu()
                case 5: self.cash_menu()
                case 0:
                    print("Sistema encerrado com segurança.")
                    return
                case _: self.message("Opção inválida.")

    def product_menu(self) -> None:
        while True:
            self.clear(); self.title("PRODUTOS")
            print("1 - Cadastrar produto\n2 - Listar produtos\n3 - Pesquisar produto")
            print("4 - Editar produto\n5 - Desativar produto\n0 - Voltar")
            option = self.read_option()
            if option == 0: return
            try:
                match option:
                    case 1: self.create_product()
                    case 2: self.show_products(self.service.products)
                    case 3: self.search_product()
                    case 4: self.edit_product()
                    case 5: self.deactivate_product()
                    case _: self.message("Opção inválida.")
            except BusinessError as error: self.message(str(error))

    def create_product(self) -> None:
        self.title("CADASTRAR PRODUTO")
        product = self.service.add_product(input("Nome: "), self.read_cash("Preço: R$ "), input("Categoria: "))
        self.message(f"Produto {product.product_id} cadastrado com sucesso.")

    def show_products(self, products: list[Product], pause: bool = True) -> None:
        self.title("LISTA DE PRODUTOS")
        if not products: print("Nenhum produto encontrado.")
        for product in products:
            status = "Ativo" if product.active else "Desativado"
            print(f"Código: {product.product_id} | Nome: {product.name} | Preço: {format_cash(product.price_cents)} | Categoria: {product.category} | Status: {status}")
        if pause: self.pause()

    def search_product(self) -> None:
        self.show_products(self.service.search_products(input("Nome ou categoria: ")))

    def edit_product(self) -> None:
        product = self.service.find_product(self.read_positive_int("Código do produto: "))
        print("Informe os novos dados.")
        self.service.edit_product(product.product_id, input("Nome: "), self.read_cash("Preço: R$ "), input("Categoria: "))
        self.message("Produto atualizado com sucesso.")

    def deactivate_product(self) -> None:
        product_id = self.read_positive_int("Código do produto: ")
        product = self.service.find_product(product_id)
        if self.confirm(f"Desativar '{product.name}'?"):
            self.service.deactivate_product(product_id); self.message("Produto desativado.")

    def order_menu(self) -> None:
        while True:
            self.clear(); self.title("COMANDAS")
            print("1 - Abrir comanda\n2 - Listar comandas\n3 - Adicionar produto")
            print("4 - Remover produto\n5 - Visualizar comanda\n6 - Fechar comanda\n0 - Voltar")
            option = self.read_option()
            if option == 0: return
            try:
                match option:
                    case 1: self.open_order()
                    case 2: self.list_orders()
                    case 3: self.add_order_item()
                    case 4: self.remove_order_item()
                    case 5: self.view_order()
                    case 6: self.close_order()
                    case _: self.message("Opção inválida.")
            except BusinessError as error: self.message(str(error))

    def open_order(self) -> None:
        order = self.service.open_order(self.read_positive_int("Número da comanda: "))
        self.message(f"Comanda {order.order_number} aberta com sucesso.")

    def list_orders(self) -> None:
        self.title("SITUAÇÃO DAS COMANDAS")
        open_numbers = {order.order_number for order in self.service.orders}
        for number in range(1, self.service.MAX_ORDERS + 1):
            print(f"Comanda {number:02d}: {'Aberta' if number in open_numbers else 'Disponível'}")
        self.pause()

    def add_order_item(self) -> None:
        number = self.read_positive_int("Número da comanda: ")
        self.show_products([item for item in self.service.products if item.active], pause=False)
        self.service.add_item(number, self.read_positive_int("Código do produto: "), self.read_positive_int("Quantidade: "))
        self.message("Produto adicionado à comanda.")

    def remove_order_item(self) -> None:
        number = self.read_positive_int("Número da comanda: ")
        self.print_order(self.service.find_order(number))
        self.service.remove_item(number, self.read_positive_int("Código do produto: "), self.read_positive_int("Quantidade a remover: "))
        self.message("Produto removido da comanda.")

    def view_order(self) -> None:
        self.print_order(self.service.find_order(self.read_positive_int("Número da comanda: ")))
        self.pause()

    def close_order(self) -> None:
        number = self.read_positive_int("Número da comanda: ")
        order = self.service.find_order(number); self.print_order(order)
        print("\n1 - Dinheiro | 2 - Pix | 3 - Crédito | 4 - Débito")
        payment = str(self.read_option("Forma de pagamento: "))
        if not self.confirm(f"Confirmar fechamento da comanda {number} por {format_cash(order.total_cents)}?"):
            self.message("Fechamento cancelado."); return
        sale = self.service.close_order(number, payment)
        self.message(f"Venda {sale.sale_id} concluída. A comanda {number} está disponível novamente.")

    def print_order(self, order: Order) -> None:
        self.title(f"COMANDA {order.order_number:02d}")
        if not order.items: print("Comanda sem produtos.")
        for item in order.items:
            print(f"{item.quantity}x {item.product_name} | {format_cash(item.unit_price_cents)} | Subtotal: {format_cash(item.subtotal_cents)}")
        print(f"TOTAL: {format_cash(order.total_cents)}")

    def sales_history(self) -> None:
        self.clear(); self.title("HISTÓRICO DE VENDAS")
        if not self.service.sales: print("Nenhuma venda concluída.")
        for sale in reversed(self.service.sales): self.print_sale(sale)
        self.pause()

    def print_sale(self, sale: Sale) -> None:
        when = datetime.fromisoformat(sale.closed_at).strftime("%d/%m/%Y %H:%M")
        print(f"Venda #{sale.sale_id} | Comanda {sale.order_number:02d} | {when} | {sale.payment_method} | {format_cash(sale.total_cents)}")

    def summary_menu(self) -> None:
        while True:
            self.clear(); self.title("RESUMOS")
            print("1 - Resumo do dia\n2 - Resumo da semana\n3 - Resumo do mês\n0 - Voltar")
            match self.read_option():
                case 1: self.show_summary("day", "DIA")
                case 2: self.show_summary("week", "SEMANA")
                case 3: self.show_summary("month", "MÊS")
                case 0: return
                case _: self.message("Opção inválida.")

    def show_summary(self, period: str, label: str) -> None:
        summary = self.service.period_summary(period)
        self.clear(); self.title(f"RESUMO DO {label}")
        print(f"Período: {summary['start'].strftime('%d/%m/%Y')} a {summary['end'].strftime('%d/%m/%Y')}")
        print(f"Vendas concluídas: {summary['sales_count']}")
        print(f"Faturamento: {format_cash(summary['total_cents'])}")
        print(f"Ticket médio: {format_cash(summary['average_cents'])}")
        print("\nPor forma de pagamento:")
        payments = summary["payments"]
        if not payments: print("  Sem vendas no período.")
        for method, total in payments.items(): print(f"  {method}: {format_cash(total)}")
        print("\nProdutos mais vendidos:")
        top_products = summary["top_products"]
        if not top_products: print("  Sem produtos vendidos no período.")
        for name, quantity in top_products: print(f"  {name}: {quantity} unidade(s)")
        change = summary["change_percent"]
        print("\nComparação com o período anterior:")
        print(f"  Anterior: {format_cash(summary['previous_total_cents'])}")
        if change is None: print("  Variação: indisponível (período anterior sem vendas)")
        else: print(f"  Variação: {change:+.1f}%")
        self.pause()

    def cash_menu(self) -> None:
        self.clear(); self.title("CAIXA")
        session = self.service.current_cash_session
        if session is None:
            print("O dia está fechado.\n1 - Iniciar dia\n0 - Voltar")
            if self.read_option() == 1:
                try:
                    session = self.service.open_cash(self.read_cash("Saldo inicial do caixa: R$ "))
                    self.message(f"Dia iniciado às {datetime.fromisoformat(session.opened_at).strftime('%H:%M')}.")
                except BusinessError as error: self.message(str(error))
            return
        print(f"Dia iniciado em {datetime.fromisoformat(session.opened_at).strftime('%d/%m/%Y às %H:%M')}")
        print(f"Saldo inicial: {format_cash(session.opening_balance_cents)}")
        print(f"Comandas abertas: {len(self.service.orders)}")
        print("\n1 - Finalizar dia\n0 - Voltar")
        if self.read_option() != 1: return
        if self.service.orders:
            numbers = ", ".join(str(order.order_number) for order in self.service.orders)
            self.message(f"Fechamento bloqueado. Feche as comandas: {numbers}."); return
        actual = self.read_cash("Valor contado em dinheiro no caixa: R$ ")
        if not self.confirm("Esta ação encerrará definitivamente o dia. Confirmar?"):
            self.message("Fechamento cancelado."); return
        try:
            closed = self.service.close_cash(actual)
            self.clear(); self.title("DIA FINALIZADO")
            print(f"Valor esperado: {format_cash(closed.expected_cash_cents or 0)}")
            print(f"Valor contado: {format_cash(closed.actual_cash_cents or 0)}")
            print(f"Diferença: {format_cash(closed.difference_cents or 0)}")
            self.pause()
        except BusinessError as error: self.message(str(error))

    @staticmethod
    def title(text: str) -> None:
        print(f"\n{'=' * 72}\n{text}\n{'=' * 72}")

    @staticmethod
    def clear() -> None:
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def pause() -> None:
        input("\nPressione ENTER para continuar...")

    def message(self, text: str) -> None:
        print(f"\n{text}"); self.pause()

    @staticmethod
    def read_option(prompt: str = "Escolha uma opção: ") -> int:
        try: return int(input(prompt))
        except ValueError: return -1

    @staticmethod
    def read_positive_int(prompt: str) -> int:
        while True:
            try:
                value = int(input(prompt))
                if value > 0: return value
            except ValueError: pass
            print("Digite um número inteiro maior que zero.")

    @staticmethod
    def read_cash(prompt: str) -> int:
        while True:
            try: return parse_cash(input(prompt))
            except ValueError: print("Digite um valor válido, como 10,50.")

    @staticmethod
    def confirm(question: str) -> bool:
        return input(f"{question} (S/N): ").strip().casefold() == "s"
