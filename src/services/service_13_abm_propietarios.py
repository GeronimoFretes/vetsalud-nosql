from datetime import datetime
from typing import Any

from pymongo import ReturnDocument

from src.db.mongo import get_database
from src.utils.json_tools import print_json, save_json


REQUIRED_CREATE_FIELDS = {
    "id_propietario",
    "nombre",
    "apellido",
    "dni",
    "email",
    "telefono",
    "ciudad",
    "provincia",
}

ALLOWED_UPDATE_FIELDS = {
    "nombre",
    "apellido",
    "dni",
    "email",
    "telefono",
    "ciudad",
    "provincia",
}


def _clean_document(document: dict | None) -> dict | None:
    """
    Removes MongoDB internal _id from a document so the service output
    is cleaner and easier to report.
    """
    if document is None:
        return None

    cleaned = dict(document)
    cleaned.pop("_id", None)
    return cleaned


def _validate_required_fields(data: dict[str, Any]) -> None:
    """
    Validates that all required owner fields are present and non-empty.
    """
    missing_fields = []

    for field in REQUIRED_CREATE_FIELDS:
        value = data.get(field)
        if value is None or str(value).strip() == "":
            missing_fields.append(field)

    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")


def obtener_propietario_por_id(id_propietario: str) -> dict | None:
    """
    Helper function:
    Returns an owner by id_propietario.
    """
    db = get_database()
    document = db.propietarios.find_one({"id_propietario": id_propietario})
    return _clean_document(document)


def alta_propietario(data: dict[str, Any]) -> dict:
    """
    Service 13 - Alta:
    Creates a new owner.

    MongoDB collection:
    - propietarios

    Validations:
    - Required fields must be present.
    - id_propietario must be unique.
    - dni must be unique.
    """
    db = get_database()

    _validate_required_fields(data)

    id_propietario = data["id_propietario"]
    dni = data["dni"]

    if db.propietarios.find_one({"id_propietario": id_propietario}) is not None:
        raise ValueError(f"Owner with id_propietario={id_propietario} already exists")

    if db.propietarios.find_one({"dni": dni}) is not None:
        raise ValueError(f"Owner with dni={dni} already exists")

    new_owner = {
        "id_propietario": id_propietario,
        "nombre": data["nombre"],
        "apellido": data["apellido"],
        "dni": dni,
        "email": data["email"],
        "telefono": data["telefono"],
        "ciudad": data["ciudad"],
        "provincia": data["provincia"],
        "activo": True,
        "fecha_alta": datetime.today(),
        "fecha_actualizacion": None,
        "fecha_baja": None,
    }

    db.propietarios.insert_one(new_owner)

    return obtener_propietario_por_id(id_propietario)


def modificar_propietario(id_propietario: str, cambios: dict[str, Any]) -> dict:
    """
    Service 13 - Modificación:
    Updates allowed data fields of an owner.

    MongoDB collection:
    - propietarios

    Validations:
    - Owner must exist.
    - id_propietario cannot be changed.
    - Only allowed fields can be modified.
    - If dni changes, the new dni must not belong to another owner.
    """
    db = get_database()

    existing_owner = db.propietarios.find_one({"id_propietario": id_propietario})

    if existing_owner is None:
        raise ValueError(f"Owner with id_propietario={id_propietario} does not exist")

    invalid_fields = set(cambios.keys()) - ALLOWED_UPDATE_FIELDS
    if invalid_fields:
        raise ValueError(f"Invalid update fields: {sorted(invalid_fields)}")

    if not cambios:
        raise ValueError("No update fields were provided")

    if "dni" in cambios:
        duplicated_dni_owner = db.propietarios.find_one(
            {
                "dni": cambios["dni"],
                "id_propietario": {
                    "$ne": id_propietario
                },
            }
        )

        if duplicated_dni_owner is not None:
            raise ValueError(f"Another owner already has dni={cambios['dni']}")

    update_data = dict(cambios)
    update_data["fecha_actualizacion"] = datetime.today()

    updated_owner = db.propietarios.find_one_and_update(
        {"id_propietario": id_propietario},
        {
            "$set": update_data
        },
        return_document=ReturnDocument.AFTER,
    )

    return _clean_document(updated_owner)


def baja_logica_propietario(id_propietario: str) -> dict:
    """
    Service 13 - Baja lógica:
    Performs a logical delete of an owner by setting activo=false.

    MongoDB collection:
    - propietarios

    This keeps the owner document in the database so historical references
    from patients remain valid.
    """
    db = get_database()

    existing_owner = db.propietarios.find_one({"id_propietario": id_propietario})

    if existing_owner is None:
        raise ValueError(f"Owner with id_propietario={id_propietario} does not exist")

    updated_owner = db.propietarios.find_one_and_update(
        {"id_propietario": id_propietario},
        {
            "$set": {
                "activo": False,
                "fecha_baja": datetime.today(),
                "fecha_actualizacion": datetime.today(),
            }
        },
        return_document=ReturnDocument.AFTER,
    )

    return _clean_document(updated_owner)


def main():
    """
    Demonstrates the full ABM flow with a controlled demo owner.

    The physical delete at the beginning is only used to make the demo
    repeatable. The actual baja function is logical.
    """
    db = get_database()

    demo_id = "PABM001"

    # Makes the demonstration idempotent when run multiple times.
    db.propietarios.delete_one({"id_propietario": demo_id})

    alta = alta_propietario(
        {
            "id_propietario": demo_id,
            "nombre": "Laura",
            "apellido": "Gimenez",
            "dni": "45999111",
            "email": "laura.gimenez@email.com",
            "telefono": "1122223333",
            "ciudad": "CABA",
            "provincia": "Buenos Aires",
        }
    )

    modificacion = modificar_propietario(
        demo_id,
        {
            "telefono": "1199998888",
            "email": "laura.gimenez.actualizado@email.com",
            "ciudad": "Vicente Lopez",
        },
    )

    baja = baja_logica_propietario(demo_id)

    result = {
        "alta": alta,
        "modificacion": modificacion,
        "baja_logica": baja,
    }

    print_json(result)
    save_json("service_13_abm_propietarios.json", result)


if __name__ == "__main__":
    main()