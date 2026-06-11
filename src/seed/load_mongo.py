from pathlib import Path

import pandas as pd

from src.db.mongo import get_database
from src.seed.extra_data import (
    EXTRA_CIRUGIAS,
    EXTRA_CONSULTAS,
    EXTRA_PACIENTES,
    EXTRA_PROPIETARIOS,
    EXTRA_VACUNACIONES,
    EXTRA_VETERINARIOS,
)
from src.utils.parsing import (
    clean_str,
    derive_tipo_consulta,
    parse_bool,
    parse_date,
    parse_float,
)


RAW_DIR = Path("data/raw")


def load_propietarios(db):
    df = pd.read_csv(RAW_DIR / "propietarios.csv")

    records = []
    for _, row in df.iterrows():
        records.append(
            {
                "id_propietario": clean_str(row["id_propietario"]),
                "nombre": clean_str(row["nombre"]),
                "apellido": clean_str(row["apellido"]),
                "dni": clean_str(row["dni"]),
                "email": clean_str(row["email"]),
                "telefono": clean_str(row["telefono"]),
                "ciudad": clean_str(row["ciudad"]),
                "provincia": clean_str(row["provincia"]),
                "activo": True,
            }
        )

    records.extend(EXTRA_PROPIETARIOS)

    db.propietarios.drop()
    db.propietarios.insert_many(records)

    db.propietarios.create_index("id_propietario", unique=True)
    db.propietarios.create_index("dni", unique=True)
    db.propietarios.create_index("activo")


def load_pacientes(db):
    df = pd.read_csv(RAW_DIR / "pacientes.csv")

    records = []
    for _, row in df.iterrows():
        records.append(
            {
                "id_paciente": clean_str(row["id_paciente"]),
                "nombre": clean_str(row["nombre"]),
                "especie": clean_str(row["especie"]),
                "raza": clean_str(row["raza"]),
                "fecha_nac": parse_date(row["fecha_nac"]),
                "id_propietario": clean_str(row["id_propietario"]),
                "activo": parse_bool(row["activo"]),
            }
        )

    records.extend(EXTRA_PACIENTES)

    db.pacientes.drop()
    db.pacientes.insert_many(records)

    db.pacientes.create_index("id_paciente", unique=True)
    db.pacientes.create_index("id_propietario")
    db.pacientes.create_index("activo")


def load_veterinarios(db):
    df = pd.read_csv(RAW_DIR / "veterinarios.csv")

    records = []
    for _, row in df.iterrows():
        records.append(
            {
                "id_vet": clean_str(row["id_vet"]),
                "nombre": clean_str(row["nombre"]),
                "apellido": clean_str(row["apellido"]),
                "matricula": clean_str(row["matricula"]),
                "especialidad": clean_str(row["especialidad"]),
                "sucursal": clean_str(row["sucursal"]),
                "activo": parse_bool(row["activo"]),
            }
        )

    records.extend(EXTRA_VETERINARIOS)

    db.veterinarios.drop()
    db.veterinarios.insert_many(records)

    db.veterinarios.create_index("id_vet", unique=True)
    db.veterinarios.create_index("matricula", unique=True)
    db.veterinarios.create_index("sucursal")
    db.veterinarios.create_index("activo")


def load_consultas(db):
    df = pd.read_csv(RAW_DIR / "consultas.csv")

    records = []
    for _, row in df.iterrows():
        motivo = clean_str(row["motivo"])

        records.append(
            {
                "id_consulta": clean_str(row["id_consulta"]),
                "id_paciente": clean_str(row["id_paciente"]),
                "id_vet": clean_str(row["id_vet"]),
                "fecha": parse_date(row["fecha"]),
                "motivo": motivo,
                "tipo_consulta": derive_tipo_consulta(motivo),
                "diagnostico": clean_str(row["diagnostico"]),
                "costo": parse_float(row["costo"]),
                "estado": clean_str(row["estado"]),
            }
        )

    records.extend(EXTRA_CONSULTAS)

    db.consultas.drop()
    db.consultas.insert_many(records)

    db.consultas.create_index("id_consulta", unique=True)
    db.consultas.create_index("id_paciente")
    db.consultas.create_index("id_vet")
    db.consultas.create_index("fecha")
    db.consultas.create_index("estado")
    db.consultas.create_index("diagnostico")
    db.consultas.create_index("tipo_consulta")


def load_vacunaciones(db):
    df = pd.read_csv(RAW_DIR / "vacunaciones.csv")

    records = []
    for _, row in df.iterrows():
        records.append(
            {
                "id_vacuna": clean_str(row["id_vacuna"]),
                "id_paciente": clean_str(row["id_paciente"]),
                "id_vet": clean_str(row["id_vet"]),
                "fecha_aplicacion": parse_date(row["fecha_aplicacion"]),
                "nombre_vacuna": clean_str(row["nombre_vacuna"]),
                "proxima_dosis": parse_date(row["proxima_dosis"]),
            }
        )

    records.extend(EXTRA_VACUNACIONES)

    db.vacunaciones.drop()
    db.vacunaciones.insert_many(records)

    db.vacunaciones.create_index("id_vacuna", unique=True)
    db.vacunaciones.create_index("id_paciente")
    db.vacunaciones.create_index("id_vet")
    db.vacunaciones.create_index("proxima_dosis")


def load_cirugias(db):
    db.cirugias.drop()
    db.cirugias.insert_many(EXTRA_CIRUGIAS)

    db.cirugias.create_index("id_cirugia", unique=True)
    db.cirugias.create_index("id_paciente")
    db.cirugias.create_index("id_vet")
    db.cirugias.create_index("fecha")


def load_mongo():
    db = get_database()

    load_propietarios(db)
    load_pacientes(db)
    load_veterinarios(db)
    load_consultas(db)
    load_vacunaciones(db)
    load_cirugias(db)

    print("MongoDB loaded successfully")


if __name__ == "__main__":
    load_mongo()