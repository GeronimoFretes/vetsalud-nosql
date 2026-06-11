from src.db.mongo import get_database
from src.utils.json_tools import print_json, save_json


def get_propietarios_con_mas_de_un_paciente():
    """
    Service 04:
    Returns owners with more than one registered patient.

    MongoDB collections:
    - pacientes
    - propietarios

    Main operations:
    - $group to count patients by owner
    - $match to keep owners with more than one patient
    - $lookup to attach owner data
    - $project to shape final response
    """
    db = get_database()

    pipeline = [
        {
            "$group": {
                "_id": "$id_propietario",
                "cantidad_pacientes": {"$sum": 1},
                "pacientes": {
                    "$push": {
                        "id_paciente": "$id_paciente",
                        "nombre": "$nombre",
                        "especie": "$especie",
                        "raza": "$raza",
                        "activo": "$activo",
                    }
                },
            }
        },
        {
            "$match": {
                "cantidad_pacientes": {
                    "$gt": 1
                }
            }
        },
        {
            "$lookup": {
                "from": "propietarios",
                "localField": "_id",
                "foreignField": "id_propietario",
                "as": "propietario",
            }
        },
        {
            "$unwind": "$propietario"
        },
        {
            "$project": {
                "_id": 0,
                "id_propietario": "$propietario.id_propietario",
                "propietario": {
                    "nombre": "$propietario.nombre",
                    "apellido": "$propietario.apellido",
                    "dni": "$propietario.dni",
                    "email": "$propietario.email",
                    "telefono": "$propietario.telefono",
                    "ciudad": "$propietario.ciudad",
                    "provincia": "$propietario.provincia",
                    "activo": "$propietario.activo",
                },
                "cantidad_pacientes": 1,
                "pacientes": 1,
            }
        },
        {
            "$sort": {
                "cantidad_pacientes": -1,
                "id_propietario": 1,
            }
        },
    ]

    return list(db.pacientes.aggregate(pipeline))


def main():
    result = get_propietarios_con_mas_de_un_paciente()
    print_json(result)
    save_json("service_04_propietarios_multiples_pacientes.json", result)


if __name__ == "__main__":
    main()