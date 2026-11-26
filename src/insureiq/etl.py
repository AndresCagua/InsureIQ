"""Deterministic validation and transformation for synthetic fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


class DataQualityError(ValueError):
    """Raised when required source tables are missing or malformed."""


def _read_table(raw_dir: Path, name: str, columns: list[str]) -> pd.DataFrame:
    path = raw_dir / f"{name}.csv"
    if not path.exists():
        raise DataQualityError(f"Falta la tabla requerida: {path}")
    frame = pd.read_csv(path)
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise DataQualityError(f"Columnas faltantes en {path}: {', '.join(missing)}")
    return frame


def run_etl(raw_dir: Path, processed_dir: Path) -> dict[str, int]:
    """Validate relationships, quarantine bad claims and publish typed tables."""
    customers = _read_table(raw_dir, "customers", ["customer_id", "age", "province"])
    vehicles = _read_table(raw_dir, "vehicles", ["vehicle_id", "vehicle_value_usd"])
    policies = _read_table(raw_dir, "policies", ["policy_id", "customer_id", "vehicle_id"])
    claims = _read_table(raw_dir, "claims", ["claim_id", "policy_id", "claimed_amount_usd"])

    quarantine = claims[
        (claims["claimed_amount_usd"] < 0)
        | (~claims["policy_id"].isin(policies["policy_id"]))
    ].copy()
    if not quarantine.empty:
        quarantine["rejection_reason"] = quarantine.apply(
            lambda row: (
                "negative_amount"
                if row["claimed_amount_usd"] < 0
                else "unknown_policy"
            ),
            axis=1,
        )
    valid_claims = claims.drop(index=quarantine.index).copy()

    if policies["customer_id"].isin(customers["customer_id"]).mean() != 1:
        raise DataQualityError("Hay pólizas con customer_id inexistente")
    if policies["vehicle_id"].isin(vehicles["vehicle_id"]).mean() != 1:
        raise DataQualityError("Hay pólizas con vehicle_id inexistente")

    processed_dir.mkdir(parents=True, exist_ok=True)
    tables = {
        "dim_customer": customers.drop_duplicates("customer_id"),
        "dim_vehicle": vehicles.drop_duplicates("vehicle_id"),
        "dim_policy": policies.drop_duplicates("policy_id"),
        "fact_claim": valid_claims.drop_duplicates("claim_id"),
    }
    for name, frame in tables.items():
        frame.to_csv(processed_dir / f"{name}.csv", index=False)
    quarantine.to_csv(processed_dir / "quarantine_claims.csv", index=False)
    manifest = {
        "input_counts": {
            "customers": len(customers),
            "vehicles": len(vehicles),
            "policies": len(policies),
            "claims": len(claims),
        },
        "output_counts": {name: len(frame) for name, frame in tables.items()},
        "quarantine_count": len(quarantine),
    }
    (processed_dir / "etl_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return manifest["output_counts"]
