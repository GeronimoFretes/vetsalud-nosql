from src.db.mongo import get_database
from src.utils.json_tools import print_json, save_json


def get_consultas_en_seguimiento():
    """
    Service 02:
    Returns open medical consultations in state 'Seguimiento',
    with assigned veterinarian and cost.

    MongoDB collections:
    - consultas
    - veterinarios
    - pacientes

    Main operations:
    - $match to filter consultations in Seguimiento
    - $lookup to attach veterinarian
    - $lookup to attach patient
    - $project to return relevant fields
    """
    db = get_database()

    pipeline = [
        {
            "$match": {
                "estado": "Seguimiento"
            }
        },
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
            "$project": {
                "_id": 0,
                "id_consulta": 1,
                "fecha": 1,
                "motivo": 1,
                "tipo_consulta": 1,
                "diagnostico": 1,
                "estado": 1,
                "costo": 1,
                "paciente": {
                    "id_paciente": "$paciente.id_paciente",
                    "nombre": "$paciente.nombre",
                    "especie": "$paciente.especie",
                    "raza": "$paciente.raza",
                },
                "veterinario": {
                    "id_vet": "$veterinario.id_vet",
                    "nombre": "$veterinario.nombre",
                    "apellido": "$veterinario.apellido",
                    "matricula": "$veterinario.matricula",
                    "especialidad": "$veterinario.especialidad",
                    "sucursal": "$veterinario.sucursal",
                },
            }
        },
        {
            "$sort": {
                "fecha": -1
            }
        },
    ]

    return list(db.consultas.aggregate(pipeline))


def main():
    result = get_consultas_en_seguimiento()
    print_json(result)
    save_json("service_02_consultas_seguimiento.json", result)


if __name__ == "__main__":
    main()