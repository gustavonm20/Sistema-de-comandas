from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation


def converter_valor(valor):
    """Converte valores como '1.234,50' para Decimal('1234.50')."""
    if isinstance(valor, Decimal):
        quantia = valor
    elif isinstance(valor, (int, float)):
        quantia = Decimal(str(valor))
    else:
        texto = str(valor or "").strip().replace("R$", "").replace(" ", "")
        if not texto:
            return None

        if "," in texto:
            texto = texto.replace(".", "").replace(",", ".")

        try:
            quantia = Decimal(texto)
        except InvalidOperation:
            return None

    if not quantia.is_finite() or quantia.copy_abs() > Decimal("99999999.99"):
        return None
    try:
        return quantia.quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


def formatar_valor(valor):
    quantia = converter_valor(valor) or Decimal("0.00")
    formatado = f"{quantia:,.2f}"
    formatado = formatado.replace(",", "TEMPORARIO").replace(".", ",").replace("TEMPORARIO", ".")
    return f"R$ {formatado}"


def formatar_data_hora(valor):
    if valor is None:
        return "—"

    if isinstance(valor, str):
        try:
            valor = datetime.fromisoformat(valor)
        except ValueError:
            return valor

    return valor.strftime("%H:%M  %d/%m/%Y")


def normalizar_nome(valor):
    return " ".join(str(valor or "").strip().lower().split())


def obter_intervalo_periodo(periodo, hoje=None):
    dia_atual = hoje or date.today()

    if periodo == "semanal":
        data_inicio = dia_atual - timedelta(days=dia_atual.weekday())
        data_fim = data_inicio + timedelta(days=7)
        rotulo = "Esta semana"
    elif periodo == "mensal":
        data_inicio = dia_atual.replace(day=1)
        if data_inicio.month == 12:
            data_fim = data_inicio.replace(year=data_inicio.year + 1, month=1)
        else:
            data_fim = data_inicio.replace(month=data_inicio.month + 1)
        rotulo = "Este mês"
    else:
        periodo = "diario"
        data_inicio = dia_atual
        data_fim = dia_atual + timedelta(days=1)
        rotulo = "Hoje"

    duracao = data_fim - data_inicio
    if periodo == "mensal":
        inicio_anterior = (data_inicio - timedelta(days=1)).replace(day=1)
    else:
        inicio_anterior = data_inicio - duracao

    return {
        "periodo": periodo,
        "rotulo": rotulo,
        "inicio": datetime.combine(data_inicio, time.min),
        "fim": datetime.combine(data_fim, time.min),
        "inicio_anterior": datetime.combine(inicio_anterior, time.min),
    }
