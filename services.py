from datetime import datetime
from decimal import Decimal

import mysql.connector

from database import fetch_all, fetch_one, get_database
from utils import get_period_range, normalize_name, parse_money


class ServiceError(Exception):
    pass


def record_audit(cursor, action, entity_type, entity_id=None, detail=None):
    cursor.execute(
        """
        INSERT INTO audit_logs (actor, action, entity_type, entity_id, detail)
        VALUES (%s, %s, %s, %s, %s)
        """,
        ("local-admin", action, entity_type, entity_id, detail),
    )


def execute_with_audit(query, parameters, action, entity_type, entity_id=None, detail=None):
    database = get_database()
    cursor = database.cursor()
    try:
        database.start_transaction()
        cursor.execute(query, parameters)
        created_id = cursor.lastrowid
        affected_rows = cursor.rowcount
        if created_id or affected_rows > 0:
            record_audit(cursor, action, entity_type, entity_id or created_id, detail)
        database.commit()
        return created_id, affected_rows
    except Exception:
        database.rollback()
        raise
    finally:
        cursor.close()


def get_dashboard():
    metrics = fetch_one(
        """
        SELECT
            (SELECT COUNT(*) FROM orders WHERE status = 'open') AS open_orders,
            COUNT(sale_id) AS completed_sales,
            COALESCE(SUM(total_amount), 0) AS revenue,
            COALESCE(AVG(total_amount), 0) AS average_ticket
        FROM sales
        WHERE DATE(sold_at) = CURDATE()
        """
    )
    latest_orders = fetch_all(
        """
        SELECT o.order_id, c.card_number, o.service_label, o.opened_at,
               COALESCE(SUM(i.quantity * i.unit_price), 0) AS total
        FROM orders o
        JOIN command_cards c ON c.card_id = o.card_id
        LEFT JOIN order_items i ON i.order_id = o.order_id
        WHERE o.status = 'open'
        GROUP BY o.order_id, c.card_number, o.service_label, o.opened_at
        ORDER BY o.opened_at DESC
        LIMIT 5
        """
    )
    hourly_rows = fetch_all(
        """
        SELECT HOUR(sold_at) AS sale_hour, SUM(total_amount) AS revenue
        FROM sales
        WHERE DATE(sold_at) = CURDATE()
        GROUP BY HOUR(sold_at)
        ORDER BY sale_hour
        """
    )
    hourly_values = {int(row["sale_hour"]): row["revenue"] for row in hourly_rows}
    maximum = max((Decimal(str(value)) for value in hourly_values.values()), default=Decimal("0"))
    trend = []
    for hour in range(8, 21):
        value = Decimal(str(hourly_values.get(hour, 0)))
        height = int((value / maximum) * 100) if maximum > 0 else 0
        trend.append({"label": f"{hour:02d}h", "value": value, "height": max(height, 4) if value else 2})

    return {
        "metrics": metrics,
        "latest_orders": latest_orders,
        "trend": trend,
    }


def list_categories():
    return fetch_all("SELECT category_id, name, active FROM categories ORDER BY name")


def list_products(search="", category_id=None, status="all"):
    conditions = ["1 = 1"]
    parameters = []

    if search:
        conditions.append("LOWER(p.name) LIKE %s")
        parameters.append(f"%{normalize_name(search)}%")
    if category_id:
        conditions.append("p.category_id = %s")
        parameters.append(category_id)
    if status == "active":
        conditions.append("p.active = TRUE")
    elif status == "inactive":
        conditions.append("p.active = FALSE")

    return fetch_all(
        f"""
        SELECT p.product_id, p.name, p.price, p.active,
               p.category_id, c.name AS category_name
        FROM products p
        JOIN categories c ON c.category_id = p.category_id
        WHERE {' AND '.join(conditions)}
        ORDER BY p.active DESC, p.name
        """,
        tuple(parameters),
    )


def get_product(product_id):
    product = fetch_one(
        """
        SELECT p.product_id, p.name, p.price, p.active,
               p.category_id, c.name AS category_name
        FROM products p
        JOIN categories c ON c.category_id = p.category_id
        WHERE p.product_id = %s
        """,
        (product_id,),
    )
    if not product:
        raise ServiceError("Produto não encontrado.")
    return product


def validate_product(name, price_text, category_id):
    clean_name = " ".join(str(name or "").strip().split())
    price = parse_money(price_text)
    try:
        category_id = int(category_id)
    except (TypeError, ValueError):
        category_id = 0

    if not 2 <= len(clean_name) <= 100:
        raise ServiceError("O nome do produto deve ter entre 2 e 100 caracteres.")
    if price is None or price <= 0:
        raise ServiceError("O preço precisa ser maior que zero.")
    category = fetch_one(
        "SELECT category_id FROM categories WHERE category_id = %s AND active = TRUE",
        (category_id,),
    )
    if not category:
        raise ServiceError("Selecione uma categoria ativa.")
    return clean_name, price, category_id


def create_product(name, price_text, category_id):
    clean_name, price, category_id = validate_product(name, price_text, category_id)
    try:
        product_id, _ = execute_with_audit(
            """
            INSERT INTO products (name, normalized_name, price, category_id, active)
            VALUES (%s, %s, %s, %s, TRUE)
            """,
            (clean_name, normalize_name(clean_name), price, category_id),
            "product.created",
            "product",
            detail=clean_name,
        )
        return product_id
    except mysql.connector.IntegrityError as error:
        raise ServiceError("Já existe um produto com esse nome.") from error


def update_product(product_id, name, price_text, category_id):
    get_product(product_id)
    clean_name, price, category_id = validate_product(name, price_text, category_id)
    try:
        execute_with_audit(
            """
            UPDATE products
            SET name = %s, normalized_name = %s, price = %s, category_id = %s
            WHERE product_id = %s
            """,
            (clean_name, normalize_name(clean_name), price, category_id, product_id),
            "product.updated",
            "product",
            product_id,
            clean_name,
        )
    except mysql.connector.IntegrityError as error:
        raise ServiceError("Já existe outro produto com esse nome.") from error


def set_product_status(product_id, active):
    product = get_product(product_id)
    if bool(product["active"]) == active:
        raise ServiceError("O produto já está com esse status.")
    execute_with_audit(
        "UPDATE products SET active = %s WHERE product_id = %s",
        (active, product_id),
        "product.activated" if active else "product.deactivated",
        "product",
        product_id,
        product["name"],
    )


def list_command_cards(status="all"):
    conditions = ["1 = 1"]
    if status == "available":
        conditions.append("c.active = TRUE AND o.order_id IS NULL")
    elif status == "open":
        conditions.append("o.order_id IS NOT NULL")
    elif status == "inactive":
        conditions.append("c.active = FALSE")

    return fetch_all(
        f"""
        SELECT c.card_id, c.card_number, c.active, o.order_id,
               o.service_label, o.opened_at,
               COALESCE(SUM(i.quantity * i.unit_price), 0) AS total
        FROM command_cards c
        LEFT JOIN orders o ON o.card_id = c.card_id AND o.status = 'open'
        LEFT JOIN order_items i ON i.order_id = o.order_id
        WHERE {' AND '.join(conditions)}
        GROUP BY c.card_id, c.card_number, c.active,
                 o.order_id, o.service_label, o.opened_at
        ORDER BY c.card_number
        """
    )


def create_command_card(card_number):
    card_number = str(card_number or "").strip()
    if len(card_number) != 4 or not card_number.isascii() or not card_number.isdigit():
        raise ServiceError("O número da comanda deve possuir quatro dígitos.")
    try:
        execute_with_audit(
            "INSERT INTO command_cards (card_number, active) VALUES (%s, TRUE)",
            (card_number,),
            "command_card.created",
            "command_card",
            detail=card_number,
        )
    except mysql.connector.IntegrityError as error:
        raise ServiceError("Já existe uma comanda com esse número.") from error


def set_command_card_status(card_id, active):
    card = fetch_one(
        """
        SELECT c.card_number,
               (SELECT order_id FROM orders WHERE card_id = c.card_id AND status = 'open' LIMIT 1) AS open_order_id
        FROM command_cards c
        WHERE c.card_id = %s
        """,
        (card_id,),
    )
    if not card:
        raise ServiceError("Cartão de comanda não encontrado.")
    if not active and card["open_order_id"]:
        raise ServiceError("Feche a comanda antes de desativar esse cartão.")
    execute_with_audit(
        "UPDATE command_cards SET active = %s WHERE card_id = %s",
        (active, card_id),
        "command_card.activated" if active else "command_card.deactivated",
        "command_card",
        card_id,
        card["card_number"],
    )


def get_open_operation():
    operation = fetch_one(
        """
        SELECT d.*,
               d.opening_cash + COALESCE((
                   SELECT SUM(s.total_amount)
                   FROM sales s
                   JOIN orders o ON o.order_id = s.order_id
                   WHERE o.operation_id = d.operation_id
                     AND s.payment_method = 'cash'
               ), 0) AS expected_cash_live
        FROM daily_operations d
        WHERE d.status = 'open'
        ORDER BY d.operation_id DESC
        LIMIT 1
        """
    )
    return operation


def open_operation(opening_cash_text):
    opening_cash = parse_money(opening_cash_text)
    if opening_cash is None or opening_cash < 0:
        raise ServiceError("Informe um valor inicial válido.")
    try:
        execute_with_audit(
            "INSERT INTO daily_operations (status, opening_cash) VALUES ('open', %s)",
            (opening_cash,),
            "operation.opened",
            "daily_operation",
            detail=str(opening_cash),
        )
    except mysql.connector.IntegrityError as error:
        raise ServiceError("Já existe um dia em andamento.") from error


def close_operation(counted_cash_text, discrepancy_note):
    counted_cash = parse_money(counted_cash_text)
    note = " ".join(str(discrepancy_note or "").strip().split())
    if len(note) > 255:
        raise ServiceError("A observação deve ter no máximo 255 caracteres.")
    if counted_cash is None or counted_cash < 0:
        raise ServiceError("Informe o valor contado no caixa.")

    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        database.start_transaction()
        cursor.execute(
            "SELECT * FROM daily_operations WHERE status = 'open' ORDER BY operation_id DESC LIMIT 1 FOR UPDATE"
        )
        operation = cursor.fetchone()
        if not operation:
            raise ServiceError("Não existe um dia em andamento.")

        cursor.execute("SELECT COUNT(*) AS total FROM orders WHERE status = 'open'")
        if cursor.fetchone()["total"] > 0:
            raise ServiceError("Feche todas as comandas antes de finalizar o dia.")

        cursor.execute(
            """
            SELECT COALESCE(SUM(s.total_amount), 0) AS cash_sales
            FROM sales s
            JOIN orders o ON o.order_id = s.order_id
            WHERE o.operation_id = %s AND s.payment_method = 'cash'
            """,
            (operation["operation_id"],),
        )
        cash_sales = Decimal(str(cursor.fetchone()["cash_sales"]))
        expected_cash = Decimal(str(operation["opening_cash"])) + cash_sales
        difference = counted_cash - expected_cash
        if difference != 0 and len(note) < 5:
            raise ServiceError("Explique a diferença encontrada no caixa.")

        cursor.execute(
            """
            UPDATE daily_operations
            SET status = 'closed', expected_cash = %s, counted_cash = %s,
                difference_amount = %s, discrepancy_note = %s, closed_at = CURRENT_TIMESTAMP
            WHERE operation_id = %s
            """,
            (expected_cash, counted_cash, difference, note or None, operation["operation_id"]),
        )
        record_audit(cursor, "operation.closed", "daily_operation", operation["operation_id"], str(difference))
        database.commit()
    except Exception:
        database.rollback()
        raise
    finally:
        cursor.close()


def list_open_orders(service_type="all"):
    condition = ""
    parameters = ()
    if service_type in {"table", "counter", "pickup"}:
        condition = "AND o.service_type = %s"
        parameters = (service_type,)
    return fetch_all(
        f"""
        SELECT o.order_id, c.card_number, o.service_type, o.service_label,
               o.opened_at, COALESCE(SUM(i.quantity * i.unit_price), 0) AS total,
               COALESCE(SUM(i.quantity), 0) AS item_count
        FROM orders o
        JOIN command_cards c ON c.card_id = o.card_id
        LEFT JOIN order_items i ON i.order_id = o.order_id
        WHERE o.status = 'open' {condition}
        GROUP BY o.order_id, c.card_number, o.service_type, o.service_label, o.opened_at
        ORDER BY o.opened_at
        """,
        parameters,
    )


def create_order(card_id, service_type, service_label="", note=""):
    try:
        card_id = int(card_id)
    except (TypeError, ValueError):
        raise ServiceError("Selecione uma comanda disponível.")
    if service_type not in {"table", "counter", "pickup"}:
        raise ServiceError("Selecione um tipo de atendimento.")

    service_label = " ".join(str(service_label or "").strip().split())
    note = " ".join(str(note or "").strip().split())
    if service_type == "table" and not service_label:
        raise ServiceError("Informe o número ou a identificação da mesa.")
    if service_type == "table":
        service_label = f"Mesa {service_label.removeprefix('Mesa ').removeprefix('mesa ')}"
    elif not service_label:
        service_label = "Balcão" if service_type == "counter" else "Retirada"
    if len(service_label) > 100 or len(note) > 255:
        raise ServiceError("Use até 100 caracteres na identificação e 255 na observação.")

    operation = get_open_operation()
    if not operation:
        raise ServiceError("Inicie o dia antes de abrir uma comanda.")
    card = fetch_one(
        "SELECT card_id FROM command_cards WHERE card_id = %s AND active = TRUE",
        (card_id,),
    )
    if not card:
        raise ServiceError("A comanda selecionada está indisponível.")

    try:
        order_id, _ = execute_with_audit(
            """
            INSERT INTO orders
                (card_id, operation_id, service_type, service_label, note, status)
            VALUES (%s, %s, %s, %s, %s, 'open')
            """,
            (card_id, operation["operation_id"], service_type, service_label, note or None),
            "order.opened",
            "order",
            detail=service_label,
        )
        return order_id
    except mysql.connector.IntegrityError as error:
        raise ServiceError("Essa comanda já está aberta.") from error


def get_order(order_id):
    order = fetch_one(
        """
        SELECT o.*, c.card_number,
               COALESCE((
                   SELECT SUM(i.quantity * i.unit_price)
                   FROM order_items i
                   WHERE i.order_id = o.order_id
               ), 0) AS total,
               COALESCE((
                   SELECT SUM(i.quantity)
                   FROM order_items i
                   WHERE i.order_id = o.order_id
               ), 0) AS item_count
        FROM orders o
        JOIN command_cards c ON c.card_id = o.card_id
        WHERE o.order_id = %s
        """,
        (order_id,),
    )
    if not order:
        raise ServiceError("Comanda não encontrada.")
    order["items"] = fetch_all(
        """
        SELECT order_item_id AS item_id, product_id, product_name_snapshot, category_name_snapshot,
               unit_price, quantity, quantity * unit_price AS line_total
        FROM order_items
        WHERE order_id = %s
        ORDER BY order_item_id
        """,
        (order_id,),
    )
    return order


def add_order_item(order_id, product_id, quantity):
    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except (TypeError, ValueError):
        raise ServiceError("Selecione um produto e uma quantidade válida.")
    if quantity < 1 or quantity > 99:
        raise ServiceError("A quantidade deve ficar entre 1 e 99.")

    order = get_order(order_id)
    if order["status"] != "open":
        raise ServiceError("Essa comanda já foi fechada.")
    existing_quantity = sum(item["quantity"] for item in order["items"] if item["product_id"] == product_id)
    if existing_quantity + quantity > 99:
        raise ServiceError("A quantidade total do produto deve ficar entre 1 e 99.")
    product = fetch_one(
        """
        SELECT p.product_id, p.name, p.price, p.active, c.name AS category_name
        FROM products p
        JOIN categories c ON c.category_id = p.category_id
        WHERE p.product_id = %s
        """,
        (product_id,),
    )
    if not product or not product["active"]:
        raise ServiceError("O produto selecionado está indisponível.")

    execute_with_audit(
        """
        INSERT INTO order_items
            (order_id, product_id, product_name_snapshot, category_name_snapshot, unit_price, quantity)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
        """,
        (
            order_id,
            product_id,
            product["name"],
            product["category_name"],
            product["price"],
            quantity,
        ),
        "order.item_added",
        "order",
        order_id,
        product["name"],
    )


def update_order_item(order_id, item_id, quantity):
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        raise ServiceError("Informe uma quantidade válida.")
    if quantity < 1 or quantity > 99:
        raise ServiceError("A quantidade deve ficar entre 1 e 99.")
    order = get_order(order_id)
    if order["status"] != "open":
        raise ServiceError("Essa comanda já foi fechada.")
    item = next((item for item in order["items"] if item["item_id"] == item_id), None)
    if item is None:
        raise ServiceError("Item não encontrado.")
    if item["quantity"] == quantity:
        return
    _, affected = execute_with_audit(
        "UPDATE order_items SET quantity = %s WHERE order_item_id = %s AND order_id = %s",
        (quantity, item_id, order_id),
        "order.item_updated",
        "order",
        order_id,
        str(item_id),
    )
    if affected == 0:
        raise ServiceError("Item não encontrado.")


def remove_order_item(order_id, item_id):
    order = get_order(order_id)
    if order["status"] != "open":
        raise ServiceError("Essa comanda já foi fechada.")
    _, affected = execute_with_audit(
        "DELETE FROM order_items WHERE order_item_id = %s AND order_id = %s",
        (item_id, order_id),
        "order.item_removed",
        "order",
        order_id,
        str(item_id),
    )
    if affected == 0:
        raise ServiceError("Item não encontrado.")


def close_order(order_id, payment_method, cash_received_text=None):
    if payment_method not in {"cash", "pix", "debit", "credit"}:
        raise ServiceError("Selecione uma forma de pagamento.")

    database = get_database()
    cursor = database.cursor(dictionary=True)
    try:
        database.start_transaction()
        cursor.execute(
            """
            SELECT o.order_id, o.status, c.card_number
            FROM orders o
            JOIN command_cards c ON c.card_id = o.card_id
            WHERE o.order_id = %s
            FOR UPDATE
            """,
            (order_id,),
        )
        order = cursor.fetchone()
        if not order:
            raise ServiceError("Comanda não encontrada.")
        if order["status"] != "open":
            raise ServiceError("Essa comanda já foi fechada.")

        cursor.execute(
            "SELECT COALESCE(SUM(quantity * unit_price), 0) AS total FROM order_items WHERE order_id = %s",
            (order_id,),
        )
        total = Decimal(str(cursor.fetchone()["total"]))
        if total <= 0:
            raise ServiceError("Adicione pelo menos um produto antes de fechar a comanda.")

        cash_received = None
        change_amount = None
        if payment_method == "cash":
            cash_received = parse_money(cash_received_text)
            if cash_received is None or cash_received < total:
                raise ServiceError("O valor recebido deve ser igual ou maior que o total.")
            change_amount = cash_received - total

        cursor.execute(
            """
            INSERT INTO sales
                (order_id, card_number_snapshot, total_amount, payment_method, cash_received, change_amount)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (order_id, order["card_number"], total, payment_method, cash_received, change_amount),
        )
        sale_id = cursor.lastrowid
        cursor.execute(
            "UPDATE orders SET status = 'closed', closed_at = CURRENT_TIMESTAMP WHERE order_id = %s",
            (order_id,),
        )
        record_audit(cursor, "order.closed", "order", order_id, payment_method)
        database.commit()
        return sale_id
    except mysql.connector.IntegrityError as error:
        database.rollback()
        raise ServiceError("O pagamento dessa comanda já foi registrado.") from error
    except Exception:
        database.rollback()
        raise
    finally:
        cursor.close()


def list_sales(search="", payment_method="all", date_from="", date_to=""):
    for value in (date_from, date_to):
        if value:
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except ValueError as error:
                raise ServiceError("Informe datas válidas no formato AAAA-MM-DD.") from error
    if date_from and date_to and date_from > date_to:
        raise ServiceError("A data inicial não pode ser posterior à data final.")
    conditions = ["1 = 1"]
    parameters = []
    digits = "".join(character for character in search if character.isdigit())
    if digits:
        conditions.append("(s.card_number_snapshot LIKE %s OR CAST(s.sale_id AS CHAR) LIKE %s)")
        parameters.extend((f"%{digits}%", f"%{digits}%"))
    if payment_method in {"cash", "pix", "debit", "credit"}:
        conditions.append("s.payment_method = %s")
        parameters.append(payment_method)
    if date_from:
        conditions.append("DATE(s.sold_at) >= %s")
        parameters.append(date_from)
    if date_to:
        conditions.append("DATE(s.sold_at) <= %s")
        parameters.append(date_to)

    return fetch_all(
        f"""
        SELECT s.sale_id, s.order_id, s.card_number_snapshot, s.total_amount,
               s.payment_method, s.sold_at, o.service_label
        FROM sales s
        JOIN orders o ON o.order_id = s.order_id
        WHERE {' AND '.join(conditions)}
        ORDER BY s.sold_at DESC
        """,
        tuple(parameters),
    )


def get_sale(sale_id):
    sale = fetch_one(
        """
        SELECT s.*, o.service_label, o.opened_at, o.closed_at
        FROM sales s
        JOIN orders o ON o.order_id = s.order_id
        WHERE s.sale_id = %s
        """,
        (sale_id,),
    )
    if not sale:
        raise ServiceError("Venda não encontrada.")
    sale["items"] = fetch_all(
        """
        SELECT product_name_snapshot, category_name_snapshot,
               unit_price, quantity, quantity * unit_price AS line_total
        FROM order_items
        WHERE order_id = %s
        ORDER BY order_item_id
        """,
        (sale["order_id"],),
    )
    return sale


def get_report(period):
    period_data = get_period_range(period)
    parameters = (period_data["start"], period_data["end"])
    metrics = fetch_one(
        """
        SELECT COUNT(*) AS completed_sales,
               COALESCE(SUM(total_amount), 0) AS revenue,
               COALESCE(AVG(total_amount), 0) AS average_ticket
        FROM sales
        WHERE sold_at >= %s AND sold_at < %s
        """,
        parameters,
    )
    previous = fetch_one(
        """
        SELECT COALESCE(SUM(total_amount), 0) AS revenue
        FROM sales
        WHERE sold_at >= %s AND sold_at < %s
        """,
        (period_data["previous_start"], period_data["start"]),
    )

    if period_data["period"] == "daily":
        trend_query = """
            SELECT CONCAT(LPAD(HOUR(sold_at), 2, '0'), 'h') AS label,
                   COUNT(*) AS sales, SUM(total_amount) AS revenue
            FROM sales
            WHERE sold_at >= %s AND sold_at < %s
            GROUP BY HOUR(sold_at)
            ORDER BY HOUR(sold_at)
        """
    else:
        trend_query = """
            SELECT DATE_FORMAT(DATE(sold_at), '%d/%m') AS label,
                   COUNT(*) AS sales, SUM(total_amount) AS revenue
            FROM sales
            WHERE sold_at >= %s AND sold_at < %s
            GROUP BY DATE(sold_at)
            ORDER BY DATE(sold_at)
        """

    trend = fetch_all(trend_query, parameters)
    maximum = max((Decimal(str(row["revenue"])) for row in trend), default=Decimal("0"))
    for row in trend:
        value = Decimal(str(row["revenue"]))
        row["height"] = int((value / maximum) * 100) if maximum > 0 else 0

    payment_methods = fetch_all(
        """
        SELECT payment_method, COUNT(*) AS sales, SUM(total_amount) AS revenue
        FROM sales
        WHERE sold_at >= %s AND sold_at < %s
        GROUP BY payment_method
        ORDER BY revenue DESC
        """,
        parameters,
    )
    top_products = fetch_all(
        """
        SELECT i.product_name_snapshot AS name, SUM(i.quantity) AS quantity,
               SUM(i.quantity * i.unit_price) AS revenue
        FROM sales s
        JOIN order_items i ON i.order_id = s.order_id
        WHERE s.sold_at >= %s AND s.sold_at < %s
        GROUP BY i.product_name_snapshot
        ORDER BY quantity DESC, revenue DESC
        LIMIT 5
        """,
        parameters,
    )

    revenue = Decimal(str(metrics["revenue"]))
    previous_revenue = Decimal(str(previous["revenue"]))
    comparison = None
    if previous_revenue > 0:
        comparison = ((revenue - previous_revenue) / previous_revenue) * 100

    return {
        "period": period_data["period"],
        "label": period_data["label"],
        "metrics": metrics,
        "comparison": comparison,
        "trend": trend,
        "payment_methods": payment_methods,
        "top_products": top_products,
    }


def get_establishment():
    return fetch_one("SELECT * FROM establishments WHERE establishment_id = 1")


def update_establishment(name, email, business_type):
    name = " ".join(str(name or "").strip().split())
    email = str(email or "").strip().lower()
    business_type = " ".join(str(business_type or "").strip().split())
    if (not 2 <= len(name) <= 120 or "@" not in email or "." not in email
            or len(email) > 150 or not 2 <= len(business_type) <= 100):
        raise ServiceError("Revise os dados do estabelecimento.")
    execute_with_audit(
        """
        UPDATE establishments
        SET name = %s, email = %s, business_type = %s
        WHERE establishment_id = 1
        """,
        (name, email, business_type),
        "establishment.updated",
        "establishment",
        1,
        name,
    )
