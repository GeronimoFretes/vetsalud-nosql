from datetime import datetime, timedelta

from src.db.mongo import get_database
from src.utils.json_tools import print_json, save_json


def get_propietarios_sin_consultas_ultimo_anio(reference_date: datetime | None = None):
    """
    Service 12:
    Returns owners with no consultations registered in the last year
    for any of their patients.

    MongoDB collections:
    - propietarios
    - pacientes
    - consultas

    Main operations:
    - $lookup to attach patients to each owner
    - $lookup with pipeline to attach recent consultations for those patients
    - $match to keep only owners with zero recent consultations
    - $project to shape the final response
    """
    db = get_database()

    if reference_date is None:
        reference_date = datetime.today()

    cutoff_date = reference_date - timedelta(days=365)

    pipeline = [
        {
            "$match": {
                "activo": True
            }
        },
        {
            "$lookup": {
                "from": "pacientes",
                "localField": "id_propietario",
                "foreignField": "id_propietario",
                "as": "pacientes",
            }
        },
        {
            "$lookup": {
                "from": "consultas",
                "let": {
                    "paciente_ids": "$pacientes.id_paciente"
                },
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$in": ["$id_paciente", "$$paciente_ids"]},
                                    {"$gte": ["$fecha", cutoff_date]},
                                ]
                            }
                        }
                    }
                ],
                "as": "consultas_ultimo_anio",
            }
        },
        {
            "$match": {
                "consultas_ultimo_anio": {
                    "$size": 0
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "id_propietario": 1,
                "nombre": 1,
                "apellido": 1,
                "dni": 1,
                "email": 1,
                "telefono": 1,
                "ciudad": 1,
                "provincia": 1,
                "cantidad_pacientes": {
                    "$size": "$pacientes"
                },
                "pacientes": {
                    "$map": {
                        "input": "$pacientes",
                        "as": "paciente",
                        "in": {
                            "id_paciente": "$$paciente.id_paciente",
                            "nombre": "$$paciente.nombre",
                            "especie": "$$paciente.especie",
                            "activo": "$$paciente.activo",
                        },
                    }
                },
            }
        },
        {
            "$sort": {
                "apellido": 1,
                "nombre": 1,
            }
        },
    ]

    return list(db.propietarios.aggregate(pipeline))


def main():
    result = get_propietarios_sin_consultas_ultimo_anio()
    print_json(result)
    save_json("service_12_propietarios_sin_consultas_anio.json", result)


if __name__ == "__main__":
    main()