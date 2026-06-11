from datetime import datetime
from typing import Any

from src.db.mongo import get_database
from src.utils.json_tools import print_json, save_json
from src.utils.parsing import derive_tipo_consulta, parse_float


REQUIRED_FIELDS = {
    "id_consulta",
    "id_paciente",
    "id_vet",
    "fecha",
    "motivo",
    "diagnostico",
    "costo",
    "estado",
}


def _clean_document(document: dict | None) -> dict | None:
    """
    Removes MongoDB internal _id from a document.
    """
    if document is None:
        return None

    cleaned = dict(document)
    cleaned.pop("_id", None)
    return cleaned


def _validate_required_fields(data: dict[str, Any]) -> None:
    """
    Validates that all required consultation fields are present and non-empty.
    """
    missing_fields = []

    for field in REQUIRED_FIELDS:
        value = data.get(field)
        if value is None or str(value).strip() == "":
            missing_fields.append(field)

    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")


def _parse_fecha(value: Any) -> datetime:
    """
    Accepts either a datetime object or a string in YYYY-MM-DD format.
    """
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        return datetime.strptime(value, "%Y-%m-%d")

    raise ValueError("fecha must be a datetime object or a YYYY-MM-DD string")


def registrar_nueva_consulta(data: dict[str, Any]) -> dict:
    """
    Service 14:
    Registers a new medical consultation after validating that the patient
    and veterinarian exist and are active.

    MongoDB collections:
    - pacientes
    - veterinarios
    - consultas

    Validations:
    - Required consultation fields must be present.
    - id_consulta must be unique.
    - id_paciente must exist.
    - id_paciente must be active.
    - id_vet must exist.
    - id_vet must be active.
    """
    db = get_database()

    _validate_required_fields(data)

    id_consulta = data["id_consulta"]
    id_paciente = data["id_paciente"]
    id_vet = data["id_vet"]

    existing_consulta = db.consultas.find_one({"id_consulta": id_consulta})
    if existing_consulta is not None:
        raise ValueError(f"Consultation with id_consulta={id_consulta} already exists")

    paciente = db.pacientes.find_one({"id_paciente": id_paciente})
    if paciente is None:
        raise ValueError(f"Patient with id_paciente={id_paciente} does not exist")

    if not paciente.get("activo", False):
        raise ValueError(f"Patient with id_paciente={id_paciente} is not active")

    veterinario = db.veterinarios.find_one({"id_vet": id_vet})
    if veterinario is None:
        raise ValueError(f"Veterinarian with id_vet={id_vet} does not exist")

    if not veterinario.get("activo", False):
        raise ValueError(f"Veterinarian with id_vet={id_vet} is not active")

    motivo = data["motivo"]

    nueva_consulta = {
        "id_consulta": id_consulta,
        "id_paciente": id_paciente,
        "id_vet": id_vet,
        "fecha": _parse_fecha(data["fecha"]),
        "motivo": motivo,
        "tipo_consulta": derive_tipo_consulta(motivo),
        "diagnostico": data["diagnostico"],
        "costo": parse_float(data["costo"]),
        "estado": data["estado"],
        "fecha_registro": datetime.today(),
    }

    db.consultas.insert_one(nueva_consulta)

    inserted = db.consultas.find_one(
        {"id_consulta": id_consulta},
        {"_id": 0},
    )

    return {
        "consulta_registrada": inserted,
        "paciente_validado": {
            "id_paciente": paciente["id_paciente"],
            "nombre": paciente["nombre"],
            "especie": paciente["especie"],
            "raza": paciente["raza"],
            "activo": paciente["activo"],
        },
        "veterinario_validado": {
            "id_vet": veterinario["id_vet"],
            "nombre": veterinario["nombre"],
            "apellido": veterinario["apellido"],
            "matricula": veterinario["matricula"],
            "especialidad": veterinario["especialidad"],
            "sucursal": veterinario["sucursal"],
            "activo": veterinario["activo"],
        },
    }


def main():
    """
    Demonstrates service 14 with a controlled consultation.

    The physical delete at the beginning is only used to make the demo
    repeatable. The actual service validates and inserts a new consultation.
    """
    db = get_database()

    demo_id = "CNUEVA001"

    # Makes the demonstration idempotent when run multiple times.
    db.consultas.delete_one({"id_consulta": demo_id})

    result = registrar_nueva_consulta(
        {
            "id_consulta": demo_id,
            "id_paciente": "PEX001",
            "id_vet": "VEX001",
            "fecha": datetime.today(),
            "motivo": "Control general por registro de nueva consulta",
            "diagnostico": "Sano",
            "costo": 4500.0,
            "estado": "Cerrada",
        }
    )

    print_json(result)
    save_json("service_14_registrar_consulta.json", result)


if __name__ == "__main__":
    main()