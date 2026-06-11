from datetime import datetime

from src.db.mongo import get_database
from src.utils.json_tools import print_json, save_json


def get_pacientes_con_vacunas_vencidas(reference_date: datetime | None = None):
    """
    Service 06:
    Returns patients with expired vaccines, meaning vaccinations whose
    next dose date is earlier than today.

    MongoDB collections:
    - vacunaciones
    - pacientes
    - veterinarios

    Main operations:
    - $match to filter expired next-dose dates
    - $lookup to attach patient data
    - $lookup to attach veterinarian data
    - $project to shape the final response
    """
    db = get_database()

    if reference_date is None:
        reference_date = datetime.today()

    today_start = datetime(reference_date.year, reference_date.month, reference_date.day)

    pipeline = [
        {
            "$match": {
                "proxima_dosis": {
                    "$lt": today_start
                }
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
            "$project": {
                "_id": 0,
                "id_vacuna": 1,
                "nombre_vacuna": 1,
                "fecha_aplicacion": 1,
                "proxima_dosis": 1,
                "paciente": {
                    "id_paciente": "$paciente.id_paciente",
                    "nombre": "$paciente.nombre",
                    "especie": "$paciente.especie",
                    "raza": "$paciente.raza",
                    "activo": "$paciente.activo",
                },
                "veterinario": {
                    "id_vet": "$veterinario.id_vet",
                    "nombre": "$veterinario.nombre",
                    "apellido": "$veterinario.apellido",
                    "matricula": "$veterinario.matricula",
                    "sucursal": "$veterinario.sucursal",
                },
            }
        },
        {
            "$sort": {
                "proxima_dosis": 1
            }
        },
    ]

    return list(db.vacunaciones.aggregate(pipeline))


def main():
    result = get_pacientes_con_vacunas_vencidas()
    print_json(result)
    save_json("service_06_vacunas_vencidas.json", result)


if __name__ == "__main__":
    main()