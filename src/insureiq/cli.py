"""Command-line checks for the reproducible project foundation."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from insureiq.bi import export_bi
from insureiq.etl import run_etl
from insureiq.forecast import forecast_from_path
from insureiq.fraud import train_from_path
from insureiq.public_data import download_iowa_crashes
from insureiq.risk import train_from_paths
from insureiq.statistics import claims_summary, quality_report
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
        "command",
        nargs="?",
        default="doctor",
        choices=(
            "doctor",
            "generate",
            "etl",
            "stats",
            "fraud",
            "risk",
            "forecast",
            "bi",
            "public-data",
        ),
    )
    parser.add_argument("--raw-dir", default="data/synthetic")
    parser.add_argument("--processed-dir", default="data/processed")
    parser.add_argument("--report", default="reports/data_quality.json")
    parser.add_argument(
        "--benchmark", default="data/raw/public_vehicle_fraud_benchmark/benchmark.csv"
    )
    parser.add_argument("--policy-path", default="data/processed/dim_policy.csv")
    parser.add_argument("--claim-path", default="data/processed/fact_claim.csv")
    args, remaining = parser.parse_known_args()
    if args.command == "generate":
        sys.argv = [sys.argv[0], *remaining]
        generate_main()
    elif args.command == "etl":
        result = run_etl(Path(args.raw_dir), Path(args.processed_dir))
        print(f"ETL completado: {result}")
    elif args.command == "stats":
        report = quality_report(Path(args.processed_dir), Path(args.report))
        claims = claims_summary(Path(args.processed_dir) / "fact_claim.csv")
        print(f"Informe estadístico generado: {len(report['tables'])} tablas; resumen: {claims}")
    elif args.command == "fraud":
        metrics = train_from_path(Path(args.benchmark), Path(args.report), target="fraud")
        print(f"Baseline de fraude entrenado: {metrics}")
    elif args.command == "risk":
        metrics = train_from_paths(
            Path(args.policy_path), Path(args.claim_path), Path(args.report)
        )
        print(f"Baselines de riesgo entrenados: {metrics}")
    elif args.command == "forecast":
        metrics = forecast_from_path(Path(args.claim_path), Path(args.report))
        print(f"Backtest de pronóstico completado: {metrics}")
    elif args.command == "bi":
        fixture = export_bi(Path(args.processed_dir), Path("dashboards/exports"))
        print(f"Exports BI generados: {fixture}")
    elif args.command == "public-data":
        metadata = download_iowa_crashes(
            Path("data/raw/public_iowa_vehicle_crashes"), Path("data/processed")
        )
        print(f"Datos públicos descargados: {metadata}")
    else:
        doctor()
