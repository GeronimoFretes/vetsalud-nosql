import json
from pathlib import Path
from typing import Any

from src.db.mongo import get_database
from src.db.redis_db import get_redis_client
from src.seed.load_redis import STOCK_INDEX_KEY
from src.utils.json_tools import print_json, save_json


OUTPUT_DIR = Path("outputs")

EXPECTED_OUTPUT_FILES = [
    "service_01_pacientes_activos.json",
    "service_02_consultas_seguimiento.json",
    "service_03_historial_paciente.json",
    "service_04_propietarios_multiples_pacientes.json",
    "service_05_veterinarios_consultas_60_dias.json",
    "service_06_vacunas_vencidas.json",
    "service_07_top_diagnosticos.json",
    "service_08_stock_bajo.json",
    "service_09_controles_bajo_costo.json",
    "service_10_pacientes_por_sucursal.json",
    "service_11_ingresos_mes_actual.json",
    "service_12_propietarios_sin_consultas_anio.json",
    "service_13_abm_propietarios.json",
    "service_14_registrar_consulta.json",
    "service_15_actualizar_stock.json",
    "run_summary.json",
]

MIN_MONGO_COUNTS = {
    "propietarios": 16,
    "pacientes": 18,
    "veterinarios": 15,
    "consultas": 18,
    "vacunaciones": 16,
    "cirugias": 10,
}

MIN_REDIS_STOCK_PRODUCTS = 16


def _check(name: str, passed: bool, details: Any = None) -> dict:
    """
    Creates a standardized validation result.
    """
    return {
        "name": name,
        "passed": passed,
        "details": details,
    }


def _load_output_json(filename: str) -> Any:
    """
    Loads one JSON output file.
    """
    path = OUTPUT_DIR / filename

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_mongo_counts() -> list[dict]:
    """
    Validates that MongoDB collections have at least the expected amount of data.
    The minimums include original CSV data plus the required extra records.
    """
    db = get_database()
    results = []

    for collection, minimum_count in MIN_MONGO_COUNTS.items():
        actual_count = db[collection].count_documents({})

        results.append(
            _check(
                name=f"MongoDB collection '{collection}' has enough records",
                passed=actual_count >= minimum_count,
                details={
                    "collection": collection,
                    "actual_count": actual_count,
                    "minimum_expected": minimum_count,
                },
            )
        )

    return results


def validate_redis_stock() -> list[dict]:
    """
    Validates that Redis contains stock products and that the low-stock index works.
    """
    redis_client = get_redis_client()

    stock_count = redis_client.zcard(STOCK_INDEX_KEY)
    low_stock_count = len(redis_client.zrangebyscore(STOCK_INDEX_KEY, "-inf", 49))

    return [
        _check(
            name="Redis stock index has enough products",
            passed=stock_count >= MIN_REDIS_STOCK_PRODUCTS,
            details={
                "actual_count": stock_count,
                "minimum_expected": MIN_REDIS_STOCK_PRODUCTS,
            },
        ),
        _check(
            name="Redis low-stock query returns at least one product",
            passed=low_stock_count > 0,
            details={
                "low_stock_count": low_stock_count,
            },
        ),
    ]


def validate_output_files() -> list[dict]:
    """
    Validates that all expected JSON output files exist and are not empty.
    """
    results = []

    for filename in EXPECTED_OUTPUT_FILES:
        path = OUTPUT_DIR / filename

        if not path.exists():
            results.append(
                _check(
                    name=f"Output file exists: {filename}",
                    passed=False,
                    details="File does not exist",
                )
            )
            continue

        try:
            content = _load_output_json(filename)
            is_not_empty = bool(content)
        except Exception as exc:
            results.append(
                _check(
                    name=f"Output file is valid JSON: {filename}",
                    passed=False,
                    details=str(exc),
                )
            )
            continue

        results.append(
            _check(
                name=f"Output file exists and is non-empty: {filename}",
                passed=is_not_empty,
                details={
                    "filename": filename,
                    "type": type(content).__name__,
                },
            )
        )

    return results


def validate_run_summary() -> list[dict]:
    """
    Validates that run_all_services completed the 15 services successfully.
    """
    path = OUTPUT_DIR / "run_summary.json"

    if not path.exists():
        return [
            _check(
                name="Run summary exists",
                passed=False,
                details="outputs/run_summary.json does not exist",
            )
        ]

    summary = _load_output_json("run_summary.json")

    total_services = summary.get("total_services")
    successful_services = summary.get("successful_services")
    failed_services = summary.get("failed_services")

    return [
        _check(
            name="Run summary includes 15 services",
            passed=total_services == 15,
            details={
                "total_services": total_services,
            },
        ),
        _check(
            name="All 15 services completed successfully",
            passed=successful_services == 15 and failed_services == 0,
            details={
                "successful_services": successful_services,
                "failed_services": failed_services,
            },
        ),
    ]


def validate_business_cases() -> list[dict]:
    """
    Validates that the seed data supports important business cases.
    This avoids the common problem of services returning empty or irrelevant results.
    """
    db = get_database()

    seguimiento_count = db.consultas.count_documents({"estado": "Seguimiento"})

    controles_baratos_count = db.consultas.count_documents(
        {
            "tipo_consulta": "Control",
            "costo": {
                "$lt": 5000
            },
        }
    )

    propietarios_multiples = list(
        db.pacientes.aggregate(
            [
                {
                    "$group": {
                        "_id": "$id_propietario",
                        "cantidad": {
                            "$sum": 1
                        },
                    }
                },
                {
                    "$match": {
                        "cantidad": {
                            "$gt": 1
                        }
                    }
                },
            ]
        )
    )

    consultas_con_diagnostico = db.consultas.count_documents(
        {
            "diagnostico": {
                "$nin": [None, ""]
            }
        }
    )

    return [
        _check(
            name="There are consultations in Seguimiento state",
            passed=seguimiento_count > 0,
            details={
                "seguimiento_count": seguimiento_count,
            },
        ),
        _check(
            name="There are Control consultations under 5000",
            passed=controles_baratos_count > 0,
            details={
                "controles_baratos_count": controles_baratos_count,
            },
        ),
        _check(
            name="There are owners with more than one patient",
            passed=len(propietarios_multiples) > 0,
            details={
                "owners_with_multiple_patients": len(propietarios_multiples),
            },
        ),
        _check(
            name="There are consultations with diagnosis values",
            passed=consultas_con_diagnostico > 0,
            details={
                "consultas_con_diagnostico": consultas_con_diagnostico,
            },
        ),
    ]


def main():
    validation_results = []

    validation_results.extend(validate_mongo_counts())
    validation_results.extend(validate_redis_stock())
    validation_results.extend(validate_output_files())
    validation_results.extend(validate_run_summary())
    validation_results.extend(validate_business_cases())

    total_checks = len(validation_results)
    passed_checks = sum(1 for result in validation_results if result["passed"])
    failed_checks = total_checks - passed_checks

    summary = {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": failed_checks,
        "all_checks_passed": failed_checks == 0,
        "checks": validation_results,
    }

    print_json(summary)
    save_json("validation_summary.json", summary)

    if failed_checks > 0:
        raise SystemExit(
            f"Validation failed: {failed_checks} checks did not pass. "
            f"See outputs/validation_summary.json"
        )

    print("\nValidation completed successfully.")
    print("Summary saved to outputs/validation_summary.json")


if __name__ == "__main__":
    main()