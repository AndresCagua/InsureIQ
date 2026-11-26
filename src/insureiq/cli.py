"""Command-line checks for the reproducible project foundation."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from insureiq.etl import run_etl
from insureiq.synthetic import main as generate_main


def doctor() -> None:
    """Check the runtime assumptions available inside the project container."""
    expected = (3, 12)
    actual = sys.version_info[:2]
    if actual != expected:
        raise SystemExit(
            f"Versión de Python incorrecta: se requiere {expected[0]}.{expected[1]}, "
            f"se encontró {actual[0]}.{actual[1]}"
        )
    print(f"Python correcto: {actual[0]}.{actual[1]}")
    print(f"Zona horaria configurada: {os.getenv('TZ', 'no configurada')}")
    print("Base reproducible InsureIQ: OK")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", nargs="?", default="doctor", choices=("doctor", "generate", "etl")
    )
    parser.add_argument("--raw-dir", default="data/synthetic")
    parser.add_argument("--processed-dir", default="data/processed")
    args, remaining = parser.parse_known_args()
    if args.command == "generate":
        sys.argv = [sys.argv[0], *remaining]
        generate_main()
    elif args.command == "etl":
        result = run_etl(Path(args.raw_dir), Path(args.processed_dir))
        print(f"ETL completado: {result}")
    else:
        doctor()
