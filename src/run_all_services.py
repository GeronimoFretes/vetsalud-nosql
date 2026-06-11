import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from src.service_registry import SERVICES
from src.utils.json_tools import save_json


def run_command(command: list[str]) -> None:
    subprocess.run(command, check=True)


def reset_databases() -> None:
    print("=" * 80)
    print("Resetting databases from CSV and extra data")
    print("=" * 80)

    run_command([sys.executable, "-m", "src.seed.seed_all"])


def run_all_services() -> list[dict]:
    results = []

    for service_number, service in SERVICES.items():
        module = service["module"]

        print("\n" + "=" * 80)
        print(f"Running service {service_number:02d}")
        print(service["description"])
        print(f"Module: {module}")
        print("=" * 80)

        started_at = datetime.today()

        try:
            run_command([sys.executable, "-m", module])
            status = "ok"
            error = None
        except subprocess.CalledProcessError as exc:
            status = "error"
            error = str(exc)

        finished_at = datetime.today()

        results.append(
            {
                "service_number": service_number,
                "description": service["description"],
                "module": module,
                "status": status,
                "error": error,
                "started_at": started_at,
                "finished_at": finished_at,
            }
        )

        if status == "error":
            raise RuntimeError(
                f"Service {service_number:02d} failed. "
                f"Stopping run_all_services."
            )

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Run all VetSalud services and generate output files."
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reload MongoDB and Redis before running all services.",
    )

    args = parser.parse_args()

    Path("outputs").mkdir(exist_ok=True)

    if args.reset:
        reset_databases()

    run_started_at = datetime.today()

    results = run_all_services()

    run_finished_at = datetime.today()

    summary = {
        "run_started_at": run_started_at,
        "run_finished_at": run_finished_at,
        "total_services": len(results),
        "successful_services": sum(1 for result in results if result["status"] == "ok"),
        "failed_services": sum(1 for result in results if result["status"] == "error"),
        "services": results,
    }

    save_json("run_summary.json", summary)

    print("\n" + "=" * 80)
    print("All services completed successfully")
    print("Summary saved to outputs/run_summary.json")
    print("=" * 80)


if __name__ == "__main__":
    main()