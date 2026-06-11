from src.db.mongo import get_database
from src.utils.json_tools import print_json, save_json


def get_top_5_diagnosticos():
    """
    Service 07:
    Returns the top 5 most frequent diagnoses.

    MongoDB collection:
    - consultas

    Main operations:
    - $match to exclude missing diagnoses
    - $group to count consultations by diagnosis
    - $sort to rank by frequency
    - $limit to keep the top 5
    - $project to shape the final response
    """
    db = get_database()

    pipeline = [
        {
            "$match": {
                "diagnostico": {
                    "$nin": [None, ""]
                }
            }
        },
        {
            "$group": {
                "_id": "$diagnostico",
                "cantidad_consultas": {
                    "$sum": 1
                },
            }
        },
        {
            "$sort": {
                "cantidad_consultas": -1,
                "_id": 1,
            }
        },
        {
            "$limit": 5
        },
        {
            "$project": {
                "_id": 0,
                "diagnostico": "$_id",
                "cantidad_consultas": 1,
            }
        },
    ]

    return list(db.consultas.aggregate(pipeline))


def main():
    result = get_top_5_diagnosticos()
    print_json(result)
    save_json("service_07_top_diagnosticos.json", result)


if __name__ == "__main__":
    main()