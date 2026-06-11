from datetime import datetime, timedelta

from src.db.mongo import get_database
from src.utils.json_tools import print_json, save_json


def get_veterinarios_activos_con_consultas_ultimos_60_dias(reference_date: datetime | None = None):
    """
    Service 05:
    Returns active veterinarians and the number of consultations performed
    in the last 60 days.

    MongoDB collections:
    - veterinarios
    - consultas

    Main operations:
    - $match to keep active veterinarians
    - $lookup with pipeline to retrieve recent consultations
    - $size to count consultations
    - $project to shape the final response

    The optional reference_date parameter makes the service easier to test.
    By default, it uses today's date.
    """
    db = get_database()

    if reference_date is None:
        reference_date = datetime.today()

    cutoff_date = reference_date - timedelta(days=60)

    pipeline = [
        {
            "$match": {
                "activo": True
            }
        },
        {
            "$lookup": {
                "from": "consultas",
                "let": {
                    "vet_id": "$id_vet"
                },
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$id_vet", "$$vet_id"]},
                                    {"$gte": ["$fecha", cutoff_date]},
                                ]
                            }
                        }
                    }
                ],
                "as": "consultas_ultimos_60_dias",
            }
        },
        {
            "$project": {
                "_id": 0,
                "id_vet": 1,
                "nombre": 1,
                "apellido": 1,
                "matricula": 1,
                "especialidad": 1,
                "sucursal": 1,
                "activo": 1,
                "cantidad_consultas_ultimos_60_dias": {
                    "$size": "$consultas_ultimos_60_dias"
                },
            }
        },
        {
            "$sort": {
                "cantidad_consultas_ultimos_60_dias": -1,
                "apellido": 1,
                "nombre": 1,
            }
        },
    ]

    return list(db.veterinarios.aggregate(pipeline))


def main():
    result = get_veterinarios_activos_con_consultas_ultimos_60_dias()
    print_json(result)
    save_json("service_05_veterinarios_consultas_60_dias.json", result)


if __name__ == "__main__":
    main()