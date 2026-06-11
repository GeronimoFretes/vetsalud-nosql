from datetime import datetime

from src.db.mongo import get_database
from src.utils.json_tools import print_json, save_json


def get_historial_paciente(id_paciente: str):
    """
    Service 03:
    Returns the full history of a patient, including consultations and vaccinations,
    ordered by date.

    MongoDB collections:
    - pacientes
    - consultas
    - vacunaciones

    Main operations:
    - find_one to validate and retrieve patient
    - find to retrieve consultations
    - find to retrieve vaccinations
    - Python-side normalization and sorting
    """
    db = get_database()

    paciente = db.pacientes.find_one(
        {"id_paciente": id_paciente},
        {"_id": 0},
    )

    if paciente is None:
        raise ValueError(f"No patient found with id_paciente={id_paciente}")

    consultas = list(
        db.consultas.find(
            {"id_paciente": id_paciente},
            {"_id": 0},
        )
    )

    vacunaciones = list(
        db.vacunaciones.find(
            {"id_paciente": id_paciente},
            {"_id": 0},
        )
    )

    historial = []

    for consulta in consultas:
        historial.append(
            {
                "tipo_evento": "consulta",
                "fecha": consulta.get("fecha"),
                "id_consulta": consulta.get("id_consulta"),
                "id_vet": consulta.get("id_vet"),
                "motivo": consulta.get("motivo"),
                "tipo_consulta": consulta.get("tipo_consulta"),
                "diagnostico": consulta.get("diagnostico"),
                "costo": consulta.get("costo"),
                "estado": consulta.get("estado"),
            }
        )

    for vacunacion in vacunaciones:
        historial.append(
            {
                "tipo_evento": "vacunacion",
                "fecha": vacunacion.get("fecha_aplicacion"),
                "id_vacuna": vacunacion.get("id_vacuna"),
                "id_vet": vacunacion.get("id_vet"),
                "nombre_vacuna": vacunacion.get("nombre_vacuna"),
                "proxima_dosis": vacunacion.get("proxima_dosis"),
            }
        )

    historial.sort(key=lambda event: event.get("fecha") or datetime.min)

    return {
        "paciente": paciente,
        "historial": historial,
    }


def main():
    # PEX001 was intentionally created with consultations and vaccinations.
    result = get_historial_paciente("PEX001")
    print_json(result)
    save_json("service_03_historial_paciente.json", result)


if __name__ == "__main__":
    main()