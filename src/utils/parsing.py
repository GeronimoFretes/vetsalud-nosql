from datetime import datetime, date
from typing import Any


def clean_str(value: Any) -> str | None:
    """
    Converts empty, null-like or NaN values to None.
    Otherwise returns a stripped string.
    """
    if value is None:
        return None

    text = str(value).strip()

    if text == "" or text.lower() in {"nan", "none", "null"}:
        return None

    return text


def parse_bool(value: Any) -> bool:
    """
    Parses common truthy values from CSV fields.
    """
    text = clean_str(value)

    if text is None:
        return False

    return text.lower() in {"true", "1", "si", "sí", "yes", "activo"}


def parse_int(value: Any) -> int:
    """
    Parses an integer safely from CSV-like values.
    """
    text = clean_str(value)

    if text is None:
        return 0

    return int(float(text))


def parse_float(value: Any) -> float:
    """
    Parses a float safely from CSV-like values.
    """
    text = clean_str(value)

    if text is None:
        return 0.0

    return float(text)


def parse_date(value: Any) -> datetime | None:
    """
    Parses dates in YYYY-MM-DD format.
    Stores them as datetime objects for MongoDB date filtering.
    """
    text = clean_str(value)

    if text is None:
        return None

    return datetime.strptime(text, "%Y-%m-%d")


def today_start() -> datetime:
    """
    Returns today's date at 00:00:00.
    Useful for date comparisons.
    """
    today = date.today()
    return datetime(today.year, today.month, today.day)


def derive_tipo_consulta(motivo: str | None) -> str:
    """
    Derives consultation type from motive.
    The assignment asks for type 'Control', while the CSV has motivo.
    """
    if motivo is None:
        return "Otra"

    if "control" in motivo.lower():
        return "Control"

    return "Otra"