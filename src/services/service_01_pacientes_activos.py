from src.db.mongo import get_database
from src.utils.json_tools import print_json, save_json


def get_pacientes_activos_con_propietario():
    """
    Service 01:
    Returns active patients with the complete data of their owner.

    MongoDB collections:
    - pacientes
    - propietarios

    Main operations:
    - $match to filter active patients
    - $lookup to attach owner data
    - $unwind to convert owner array into object
    - $project to shape the final response
    """
    db = get_database()

    pipeline = [
        {
            "$match": {
                "activo": True
            }
        },
        {
            "$lookup": {
                "from": "propietarios",
                "localField": "id_propietario",
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
                "id_paciente": 1,
                "nombre_paciente": "$nombre",
                "especie": 1,
                "raza": 1,
                "fecha_nac": 1,
                "activo": 1,
                "propietario": {
                    "id_propietario": "$propietario.id_propietario",
                    "nombre": "$propietario.nombre",
                    "apellido": "$propietario.apellido",
                    "dni": "$propietario.dni",
                    "email": "$propietario.email",
                    "telefono": "$propietario.telefono",
                    "ciudad": "$propietario.ciudad",
                    "provincia": "$propietario.provincia",
                    "activo": "$propietario.activo",
                },
            }
        },
        {
            "$sort": {
                "nombre_paciente": 1
            }
        },
    ]

    return list(db.pacientes.aggregate(pipeline))


def main():
    result = get_pacientes_activos_con_propietario()
    print_json(result)
    save_json("service_01_pacientes_activos.json", result)


if __name__ == "__main__":
    main()