import os
import secrets
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from database import close_database
from services import (
    ServiceError,
    add_order_item,
    close_operation,
    close_order,
    create_command_card,
    create_order,
    create_product,
    get_dashboard,
    get_establishment,
    get_open_operation,
    get_order,
    get_product,
    get_report,
    get_sale,
    list_categories,
    list_command_cards,
    list_open_orders,
    list_products,
    list_sales,
    open_operation,
    remove_order_item,
    set_command_card_status,
    set_product_status,
    update_establishment,
    update_order_item,
    update_product,
)
from utils import format_datetime, format_money


load_dotenv(Path(__file__).with_name(".env"))
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32),
    MYSQL_HOST=os.getenv("MYSQL_HOST", "127.0.0.1"),
    MYSQL_PORT=int(os.getenv("MYSQL_PORT", "3306")),
    MYSQL_USER=os.getenv("MYSQL_USER", "root"),
    MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD", ""),
    MYSQL_DATABASE=os.getenv("MYSQL_DATABASE", "comandas_db"),
)
app.teardown_appcontext(close_database)


PAYMENT_LABELS = {
    "cash": "Dinheiro",
    "pix": "Pix",
    "debit": "Débito",
    "credit": "Crédito",
}


@app.context_processor
def inject_template_helpers():
    return {
        "format_money": format_money,
        "format_datetime": format_datetime,
        "payment_label": lambda value: PAYMENT_LABELS.get(value, value),
    }


def render_page(template_name, **context):
    context.setdefault("establishment", get_establishment())
    context.setdefault("operation", get_open_operation())
    return render_template(template_name, **context)


@app.errorhandler(mysql.connector.Error)
def handle_database_error(error):
    app.logger.error("Database error: %s", error)
    return render_template("database_error.html"), 503


@app.errorhandler(ServiceError)
def handle_service_error(error):
    return render_template("error.html", message=str(error)), 400


@app.route("/")
def dashboard():
    return render_page("dashboard.html", active_page="dashboard", dashboard=get_dashboard())


@app.route("/products")
def products():
    search = request.args.get("search", "").strip()
    category_id = request.args.get("category_id", type=int)
    status = request.args.get("status", "all")
    return render_page(
        "products.html",
        active_page="products",
        products=list_products(search, category_id, status),
        categories=list_categories(),
        search=search,
        selected_category=category_id,
        selected_status=status,
    )


@app.route("/products/new", methods=["GET", "POST"])
def product_create():
    if request.method == "POST":
        try:
            create_product(request.form.get("name"), request.form.get("price"), request.form.get("category_id"))
            flash("Produto cadastrado com sucesso.", "success")
            return redirect(url_for("products"))
        except ServiceError as error:
            flash(str(error), "error")

    return render_page(
        "product_form.html",
        active_page="products",
        categories=list_categories(),
        product=None,
        page_title="Novo produto",
    )


@app.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
def product_edit(product_id):
    product = get_product(product_id)
    if request.method == "POST":
        try:
            update_product(
                product_id,
                request.form.get("name"),
                request.form.get("price"),
                request.form.get("category_id"),
            )
            flash("Produto atualizado com sucesso.", "success")
            return redirect(url_for("products"))
        except ServiceError as error:
            flash(str(error), "error")

    return render_page(
        "product_form.html",
        active_page="products",
        categories=list_categories(),
        product=product,
        page_title="Editar produto",
    )


@app.post("/products/<int:product_id>/status")
def product_status(product_id):
    try:
        active = request.form.get("active") == "true"
        set_product_status(product_id, active)
        flash("Status do produto atualizado.", "success")
    except ServiceError as error:
        flash(str(error), "error")
    return redirect(url_for("products"))


@app.route("/cards", methods=["GET", "POST"])
def cards():
    if request.method == "POST":
        try:
            create_command_card(request.form.get("card_number"))
            flash("Cartão de comanda criado.", "success")
            return redirect(url_for("cards"))
        except ServiceError as error:
            flash(str(error), "error")

    status = request.args.get("status", "all")
    return render_page(
        "cards.html",
        active_page="orders",
        cards=list_command_cards(status),
        selected_status=status,
    )


@app.post("/cards/<int:card_id>/status")
def card_status(card_id):
    try:
        active = request.form.get("active") == "true"
        set_command_card_status(card_id, active)
        flash("Status da comanda atualizado.", "success")
    except ServiceError as error:
        flash(str(error), "error")
    return redirect(url_for("cards"))


@app.route("/orders")
def orders():
    service_type = request.args.get("service_type", "all")
    return render_page(
        "orders.html",
        active_page="orders",
        orders=list_open_orders(service_type),
        selected_service=service_type,
    )


@app.route("/orders/new", methods=["GET", "POST"])
def order_create():
    if request.method == "POST":
        try:
            order_id = create_order(
                request.form.get("card_id"),
                request.form.get("service_type"),
                request.form.get("service_label"),
                request.form.get("note"),
            )
            flash("Comanda aberta com sucesso.", "success")
            return redirect(url_for("order_details", order_id=order_id))
        except ServiceError as error:
            flash(str(error), "error")

    return render_page(
        "new_order.html",
        active_page="orders",
        cards=list_command_cards("available"),
    )


@app.route("/orders/<int:order_id>")
def order_details(order_id):
    product_search = request.args.get("product_search", "").strip()
    return render_page(
        "order_details.html",
        active_page="orders",
        order=get_order(order_id),
        products=list_products(product_search, status="active"),
        product_search=product_search,
    )


@app.post("/orders/<int:order_id>/items")
def order_item_add(order_id):
    try:
        add_order_item(order_id, request.form.get("product_id"), request.form.get("quantity", 1))
        flash("Produto adicionado à comanda.", "success")
    except ServiceError as error:
        flash(str(error), "error")
    return redirect(url_for("order_details", order_id=order_id))


@app.post("/orders/<int:order_id>/items/<int:item_id>/quantity")
def order_item_update(order_id, item_id):
    try:
        update_order_item(order_id, item_id, request.form.get("quantity"))
    except ServiceError as error:
        flash(str(error), "error")
    return redirect(url_for("order_details", order_id=order_id))


@app.post("/orders/<int:order_id>/items/<int:item_id>/remove")
def order_item_remove(order_id, item_id):
    try:
        remove_order_item(order_id, item_id)
        flash("Produto removido da comanda.", "success")
    except ServiceError as error:
        flash(str(error), "error")
    return redirect(url_for("order_details", order_id=order_id))


@app.route("/orders/<int:order_id>/payment", methods=["GET", "POST"])
def payment(order_id):
    order = get_order(order_id)
    if request.method == "POST":
        try:
            sale_id = close_order(
                order_id,
                request.form.get("payment_method"),
                request.form.get("cash_received"),
            )
            flash("Pagamento registrado e comanda liberada.", "success")
            return redirect(url_for("sale_details", sale_id=sale_id))
        except ServiceError as error:
            flash(str(error), "error")

    return render_page("payment.html", active_page="orders", order=order)


@app.route("/history")
def history():
    filters = {
        "search": request.args.get("search", "").strip(),
        "payment_method": request.args.get("payment_method", "all"),
        "date_from": request.args.get("date_from", ""),
        "date_to": request.args.get("date_to", ""),
    }
    return render_page(
        "history.html",
        active_page="history",
        sales=list_sales(**filters),
        filters=filters,
    )


@app.route("/sales/<int:sale_id>")
def sale_details(sale_id):
    return render_page(
        "sale_details.html",
        active_page="history",
        sale=get_sale(sale_id),
    )


@app.route("/reports")
def reports():
    period = request.args.get("period", "daily")
    if period not in {"daily", "weekly", "monthly"}:
        period = "daily"
    return render_page(
        "reports.html",
        active_page="dashboard",
        report=get_report(period),
    )


@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        try:
            update_establishment(
                request.form.get("name"),
                request.form.get("email"),
                request.form.get("business_type"),
            )
            flash("Dados do estabelecimento atualizados.", "success")
            return redirect(url_for("account"))
        except ServiceError as error:
            flash(str(error), "error")

    return render_page("account.html", active_page="account")


@app.post("/operation/open")
def operation_open():
    try:
        open_operation(request.form.get("opening_cash"))
        flash("Dia iniciado e caixa aberto.", "success")
    except ServiceError as error:
        flash(str(error), "error")
    return redirect(url_for("account"))


@app.post("/operation/close")
def operation_close():
    try:
        close_operation(request.form.get("counted_cash"), request.form.get("discrepancy_note"))
        flash("Caixa conferido e dia finalizado.", "success")
    except ServiceError as error:
        flash(str(error), "error")
    return redirect(url_for("account"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=False)
