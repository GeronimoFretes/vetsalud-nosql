import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from bson import ObjectId


def to_json_serializable(value: Any):
    """
    Converts MongoDB/Python objects into JSON-compatible values.
    This is needed for ObjectId and datetime values.
    """
    if isinstance(value, ObjectId):
        return str(value)

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def print_json(data: Any) -> None:
    """
    Pretty-prints a Python object as JSON.
    """
    print(json.dumps(data, ensure_ascii=False, indent=2, default=to_json_serializable))


def save_json(filename: str, data: Any) -> None:
    """
    Saves a Python object into the outputs/ folder as JSON.
    """
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / filename

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2, default=to_json_serializable)