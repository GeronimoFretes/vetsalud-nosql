from datetime import datetime

from src.db.mongo import get_database
from src.utils.json_tools import print_json, save_json


def _month_range(reference_date: datetime) -> tuple[datetime, datetime]:
    """
    Returns the start of the current month and the start of the next month.
    """
    start = datetime(reference_date.year, reference_date.month, 1)

    if reference_date.month == 12:
        end = datetime(reference_date.year + 1, 1, 1)
    else:
        end = datetime(reference_date.year, reference_date.month + 1, 1)

    return start, end


def get_ingresos_totales_por_veterinario_mes_actual(reference_date: datetime | None = None):
    """
    Service 11:
    Returns total revenue by veterinarian for the current month.

    MongoDB collections:
    - consultas
    - veterinarios

    Main operations:
    - $match to filter consultations in current month
    - $group to sum revenue and count consultations by vet
    - $lookup to attach veterinarian data
    - $project to shape the final response
    """
    db = get_database()

    if reference_date is None:
        reference_date = datetime.today()

    start_month, start_next_month = _month_range(reference_date)

    pipeline = [
        {
            "$match": {
                "fecha": {
                    "$gte": start_month,
                    "$lt": start_next_month,
                }
            }
        },
        {
            "$group": {
                "_id": "$id_vet",
                "ingresos_totales": {
                    "$sum": "$costo"
                },
                "cantidad_consultas": {
                    "$sum": 1
                },
            }
        },
        {
            "$lookup": {
                "from": "veterinarios",
                "localField": "_id",
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
                "id_vet": "$_id",
                "veterinario": {
                    "nombre": "$veterinario.nombre",
                    "apellido": "$veterinario.apellido",
                    "matricula": "$veterinario.matricula",
                    "especialidad": "$veterinario.especialidad",
                    "sucursal": "$veterinario.sucursal",
                },
                "cantidad_consultas": 1,
                "ingresos_totales": 1,
            }
        },
        {
            "$sort": {
                "ingresos_totales": -1,
                "id_vet": 1,
            }
        },
    ]

    return list(db.consultas.aggregate(pipeline))


def main():
    result = get_ingresos_totales_por_veterinario_mes_actual()
    print_json(result)
    save_json("service_11_ingresos_mes_actual.json", result)


if __name__ == "__main__":
    main()