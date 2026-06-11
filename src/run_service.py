import argparse
import subprocess
import sys

from src.service_registry import SERVICES


def list_services() -> None:
    print("Available services:\n")

    for number, service in SERVICES.items():
        print(f"{number:02d}. {service['description']}")


def run_service(service_number: int) -> None:
    if service_number not in SERVICES:
        valid_numbers = ", ".join(str(number) for number in SERVICES.keys())
        raise ValueError(
            f"Invalid service number: {service_number}. "
            f"Valid numbers are: {valid_numbers}"
        )

    service = SERVICES[service_number]
    module = service["module"]

    print("=" * 80)
    print(f"Running service {service_number:02d}")
    print(service["description"])
    print(f"Module: {module}")
    print("=" * 80)

    subprocess.run(
        [sys.executable, "-m", module],
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Run one VetSalud service by number."
    )

    parser.add_argument(
        "service_number",
        nargs="?",
        type=int,
        help="Service number to run, from 1 to 15.",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List available services.",
    )

    args = parser.parse_args()

    if args.list:
        list_services()
        return

    if args.service_number is None:
        list_services()
        raise SystemExit("\nPlease provide a service number.")

    run_service(args.service_number)


if __name__ == "__main__":
    main()