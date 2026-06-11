import json
from pathlib import Path
from typing import Any


OUTPUTS_DIR = Path("outputs")
REPORT_EXAMPLES_PATH = Path("informe/ejemplos_resultados.md")


def load_json(filename: str) -> Any:
    path = OUTPUTS_DIR / filename

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def first_item(data: Any) -> Any:
    if isinstance(data, list):
        return data[0] if data else None

    if isinstance(data, dict):
        return data

    return None


def format_money(value: Any) -> str:
    try:
        return f"${float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (TypeError, ValueError):
        return str(value)


def service_01() -> str:
    item = first_item(load_json("service_01_pacientes_activos.json"))
    owner = item["propietario"]

    return (
        f"Paciente `{item['id_paciente']}`: {item['nombre_paciente']} "
        f"({item['especie']}, {item['raza']}), propietario "
        f"{owner['nombre']} {owner['apellido']}."
    )


def service_02() -> str:
    item = first_item(load_json("service_02_consultas_seguimiento.json"))
    vet = item["veterinario"]
    patient = item["paciente"]

    return (
        f"Consulta `{item['id_consulta']}` en estado `{item['estado']}`, "
        f"paciente {patient['nombre']}, veterinario "
        f"{vet['nombre']} {vet['apellido']}, costo {format_money(item['costo'])}."
    )


def service_03() -> str:
    data = load_json("service_03_historial_paciente.json")
    paciente = data["paciente"]
    historial = data["historial"]

    eventos = ", ".join(
        f"{event['tipo_evento']} {event['fecha'][:10]}"
        for event in historial[:3]
    )

    return (
        f"Paciente `{paciente['id_paciente']}`: {paciente['nombre']}. "
        f"Primeros eventos del historial: {eventos}."
    )


def service_04() -> str:
    item = first_item(load_json("service_04_propietarios_multiples_pacientes.json"))
    owner = item["propietario"]

    return (
        f"Propietario `{item['id_propietario']}`: "
        f"{owner['nombre']} {owner['apellido']}, "
        f"{item['cantidad_pacientes']} pacientes registrados."
    )


def service_05() -> str:
    item = first_item(load_json("service_05_veterinarios_consultas_60_dias.json"))

    return (
        f"Veterinario `{item['id_vet']}`: {item['nombre']} {item['apellido']}, "
        f"{item['cantidad_consultas_ultimos_60_dias']} consultas en los últimos 60 días."
    )


def service_06() -> str:
    item = first_item(load_json("service_06_vacunas_vencidas.json"))
    patient = item["paciente"]

    return (
        f"Vacuna `{item['nombre_vacuna']}` vencida para "
        f"{patient['nombre']} (`{patient['id_paciente']}`), "
        f"próxima dosis {item['proxima_dosis'][:10]}."
    )


def service_07() -> str:
    item = first_item(load_json("service_07_top_diagnosticos.json"))

    return (
        f"Diagnóstico más frecuente: `{item['diagnostico']}`, "
        f"{item['cantidad_consultas']} consultas."
    )


def service_08() -> str:
    item = first_item(load_json("service_08_stock_bajo.json"))

    return (
        f"Producto `{item['id_producto']}`: {item['nombre']}, "
        f"{item['unidades']} unidades, proveedor {item['proveedor']}."
    )


def service_09() -> str:
    item = first_item(load_json("service_09_controles_bajo_costo.json"))

    return (
        f"Consulta `{item['id_consulta']}` de tipo `{item['tipo_consulta']}`, "
        f"costo {format_money(item['costo'])}."
    )


def service_10() -> str:
    item = first_item(load_json("service_10_pacientes_por_sucursal.json"))

    return (
        f"Paciente `{item['id_paciente']}`: {item['nombre']}, "
        f"sucursal consultada {item['sucursal_consultada']}, "
        f"{item['cantidad_consultas_en_sucursal']} consulta/s."
    )


def service_11() -> str:
    item = first_item(load_json("service_11_ingresos_mes_actual.json"))
    vet = item["veterinario"]

    return (
        f"Veterinario `{item['id_vet']}`: {vet['nombre']} {vet['apellido']}, "
        f"ingresos del mes {format_money(item['ingresos_totales'])} "
        f"en {item['cantidad_consultas']} consulta/s."
    )


def service_12() -> str:
    item = first_item(load_json("service_12_propietarios_sin_consultas_anio.json"))

    return (
        f"Propietario `{item['id_propietario']}`: "
        f"{item['nombre']} {item['apellido']}, "
        f"{item['cantidad_pacientes']} paciente/s y sin consultas en el último año."
    )


def service_13() -> str:
    data = load_json("service_13_abm_propietarios.json")
    alta = data["alta"]
    baja = data["baja_logica"]

    return (
        f"Se creó el propietario `{alta['id_propietario']}` "
        f"y luego se aplicó baja lógica. Estado final: activo={baja['activo']}."
    )


def service_14() -> str:
    data = load_json("service_14_registrar_consulta.json")
    consulta = data["consulta_registrada"]
    paciente = data["paciente_validado"]
    vet = data["veterinario_validado"]

    return (
        f"Consulta `{consulta['id_consulta']}` registrada para "
        f"{paciente['nombre']} con veterinario {vet['nombre']} {vet['apellido']}."
    )


def service_15() -> str:
    data = load_json("service_15_actualizar_stock.json")
    movement = data["movimientos"][0]

    return (
        f"Consulta `{data['id_consulta']}`: producto `{movement['id_producto']}` "
        f"decrementado de {movement['unidades_antes']} a "
        f"{movement['unidades_despues']} unidades."
    )


EXAMPLE_FUNCTIONS = {
    1: service_01,
    2: service_02,
    3: service_03,
    4: service_04,
    5: service_05,
    6: service_06,
    7: service_07,
    8: service_08,
    9: service_09,
    10: service_10,
    11: service_11,
    12: service_12,
    13: service_13,
    14: service_14,
    15: service_15,
}


def main():
    lines = [
        "## 7. Resultados de ejemplo",
        "",
        "A continuación se presenta un resultado resumido por cada servicio implementado. "
        "Las salidas completas se encuentran en la carpeta `outputs/` en formato JSON.",
        "",
        "| Nº | Resultado de ejemplo |",
        "|---:|---|",
    ]

    for service_number, function in EXAMPLE_FUNCTIONS.items():
        try:
            example = function()
        except Exception as exc:
            example = f"No se pudo generar el ejemplo: {exc}"

        lines.append(f"| {service_number} | {example} |")

    REPORT_EXAMPLES_PATH.parent.mkdir(exist_ok=True)

    with REPORT_EXAMPLES_PATH.open("w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    print(f"Examples written to {REPORT_EXAMPLES_PATH}")


if __name__ == "__main__":
    main()