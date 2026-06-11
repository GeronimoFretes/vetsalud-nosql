from src.db.mongo import get_database
from src.utils.json_tools import print_json, save_json


def get_pacientes_por_sucursal_veterinario(sucursal: str):
    """
    Service 10:
    Returns all patients associated with a given branch through the veterinarian
    who attended consultations in that branch.

    MongoDB collections:
    - consultas
    - veterinarios
    - pacientes

    Main operations:
    - $lookup to attach veterinarian to each consultation
    - $match to filter by veterinarian branch
    - $lookup to attach patient
    - $group to avoid duplicate patients
    - $project to shape the final response
    """
    db = get_database()

    pipeline = [
        {
            "$lookup": {
                "from": "veterinarios",
                "localField": "id_vet",
                "foreignField": "id_vet",
                "as": "veterinario",
            }
        },
        {
            "$unwind": "$veterinario"
        },
        {
            "$match": {
                "veterinario.sucursal": sucursal
            }
        },
        {
            "$lookup": {
                "from": "pacientes",
                "localField": "id_paciente",
                "foreignField": "id_paciente",
                "as": "paciente",
            }
        },
        {
            "$unwind": "$paciente"
        },
        {
            "$group": {
                "_id": "$paciente.id_paciente",
                "paciente": {
                    "$first": "$paciente"
                },
                "sucursales": {
                    "$addToSet": "$veterinario.sucursal"
                },
                "veterinarios_que_lo_atendieron": {
                    "$addToSet": {
                        "id_vet": "$veterinario.id_vet",
                        "nombre": "$veterinario.nombre",
                        "apellido": "$veterinario.apellido",
                        "especialidad": "$veterinario.especialidad",
                    }
                },
                "cantidad_consultas_en_sucursal": {
                    "$sum": 1
                },
            }
        },
        {
            "$project": {
                "_id": 0,
                "id_paciente": "$paciente.id_paciente",
                "nombre": "$paciente.nombre",
                "especie": "$paciente.especie",
                "raza": "$paciente.raza",
                "activo": "$paciente.activo",
                "sucursal_consultada": sucursal,
                "cantidad_consultas_en_sucursal": 1,
                "veterinarios_que_lo_atendieron": 1,
            }
        },
        {
            "$sort": {
                "nombre": 1,
                "id_paciente": 1,
            }
        },
    ]

    return list(db.consultas.aggregate(pipeline))


def main():
    result = get_pacientes_por_sucursal_veterinario("Palermo")
    print_json(result)
    save_json("service_10_pacientes_por_sucursal.json", result)


if __name__ == "__main__":
    main()