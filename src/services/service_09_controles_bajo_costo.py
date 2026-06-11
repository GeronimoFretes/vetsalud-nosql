from src.db.mongo import get_database
from src.utils.json_tools import print_json, save_json


def get_consultas_control_menor_5000():
    """
    Service 09:
    Returns consultations of type 'Control' with cost lower than 5000.

    MongoDB collection:
    - consultas

    Main operations:
    - find with filters on tipo_consulta and costo
    - sort by cost and date

    Note:
    tipo_consulta is derived during data loading from the original motivo field.
    """
    db = get_database()

    query = {
        "tipo_consulta": "Control",
        "costo": {
            "$lt": 5000
        },
    }

    projection = {
        "_id": 0,
        "id_consulta": 1,
        "id_paciente": 1,
        "id_vet": 1,
        "fecha": 1,
        "motivo": 1,
        "tipo_consulta": 1,
        "diagnostico": 1,
        "costo": 1,
        "estado": 1,
    }

    return list(
        db.consultas.find(query, projection).sort(
            [
                ("costo", 1),
                ("fecha", -1),
            ]
        )
    )


def main():
    result = get_consultas_control_menor_5000()
    print_json(result)
    save_json("service_09_controles_bajo_costo.json", result)


if __name__ == "__main__":
    main()