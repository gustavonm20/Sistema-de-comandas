from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation


def parse_money(value):
    """Converte valores como '1.234,50' para Decimal('1234.50')."""
    if isinstance(value, Decimal):
        amount = value
    elif isinstance(value, (int, float)):
        amount = Decimal(str(value))
    else:
        text = str(value or "").strip().replace("R$", "").replace(" ", "")
        if not text:
            return None

        if "," in text:
            text = text.replace(".", "").replace(",", ".")

        try:
            amount = Decimal(text)
        except InvalidOperation:
            return None

    if not amount.is_finite() or amount.copy_abs() > Decimal("99999999.99"):
        return None
    try:
        return amount.quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


def format_money(value):
    amount = parse_money(value) or Decimal("0.00")
    formatted = f"{amount:,.2f}"
    formatted = formatted.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")
    return f"R$ {formatted}"


def format_datetime(value):
    if value is None:
        return "—"

    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value

    return value.strftime("%H:%M  %d/%m/%Y")


def normalize_name(value):
    return " ".join(str(value or "").strip().lower().split())


def get_period_range(period, today=None):
    current_day = today or date.today()

    if period == "weekly":
        start_date = current_day - timedelta(days=current_day.weekday())
        end_date = start_date + timedelta(days=7)
        label = "Esta semana"
    elif period == "monthly":
        start_date = current_day.replace(day=1)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)
        label = "Este mês"
    else:
        period = "daily"
        start_date = current_day
        end_date = current_day + timedelta(days=1)
        label = "Hoje"

    duration = end_date - start_date
    if period == "monthly":
        previous_start = (start_date - timedelta(days=1)).replace(day=1)
    else:
        previous_start = start_date - duration

    return {
        "period": period,
        "label": label,
        "start": datetime.combine(start_date, time.min),
        "end": datetime.combine(end_date, time.min),
        "previous_start": datetime.combine(previous_start, time.min),
    }
