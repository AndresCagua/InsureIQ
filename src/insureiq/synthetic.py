"""Deterministic synthetic data generator for the InsureIQ smoke profile."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

PROVINCES = ["Pichincha", "Guayas", "Azuay", "Manabí", "Tungurahua", "Loja"]
PRODUCTS = ["basic", "standard", "premium"]
VEHICLE_MAKES = ["Toyota", "Chevrolet", "Kia", "Hyundai", "Nissan"]


def load_config(config_path: Path) -> dict:
    """Load a generator configuration from YAML."""
    with config_path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def generate(profile: str, config_path: Path, output_dir: Path) -> dict[str, int]:
    """Generate related customers, vehicles, policies and claims."""
    config = load_config(config_path)
    rng = np.random.default_rng(int(config["seed"]))
    scale = float(config["records_scale"])
    counts = {
        "customers": max(10, round(100_000 * scale)),
        "vehicles": max(10, round(120_000 * scale)),
        "policies": max(10, round(250_000 * scale)),
    }
    counts["claims"] = max(1, round(counts["policies"] * 0.2))

    output_dir.mkdir(parents=True, exist_ok=True)
    customers = pd.DataFrame(
        {
            "customer_id": [f"CUS-{i:07d}" for i in range(1, counts["customers"] + 1)],
            "age": rng.integers(18, 76, counts["customers"]),
            "province": rng.choice(PROVINCES, counts["customers"]),
            "is_synthetic": True,
        }
    )
    vehicles = pd.DataFrame(
        {
            "vehicle_id": [f"VEH-{i:07d}" for i in range(1, counts["vehicles"] + 1)],
            "make": rng.choice(VEHICLE_MAKES, counts["vehicles"]),
            "model_year": rng.integers(2014, 2026, counts["vehicles"]),
            "vehicle_value_usd": rng.integers(8_000, 55_000, counts["vehicles"]),
            "is_synthetic": True,
        }
    )
    policy_ids = [f"POL-{i:07d}" for i in range(1, counts["policies"] + 1)]
    policies = pd.DataFrame(
        {
            "policy_id": policy_ids,
            "customer_id": rng.choice(customers["customer_id"], counts["policies"]),
            "vehicle_id": rng.choice(vehicles["vehicle_id"], counts["policies"]),
            "product": rng.choice(PRODUCTS, counts["policies"], p=[0.35, 0.5, 0.15]),
            "annual_premium_usd": rng.uniform(250, 2_400, counts["policies"]).round(2),
            "is_synthetic": True,
        }
    )
    claim_count = counts["claims"]
    claims = pd.DataFrame(
        {
            "claim_id": [f"CLM-{i:07d}" for i in range(1, claim_count + 1)],
            "policy_id": rng.choice(policy_ids, claim_count),
            "loss_date": pd.to_datetime(
                rng.integers(
                    pd.Timestamp("2021-01-01").value // 10**9,
                    pd.Timestamp("2025-12-31").value // 10**9,
                    claim_count,
                ),
                unit="s",
            ).date,
            "claimed_amount_usd": rng.gamma(shape=2.0, scale=1_200, size=claim_count).round(2),
            "is_synthetic": True,
        }
    )
    # Deliberate but traceable raw anomalies; downstream validation must quarantine them.
    anomalies = claims.head(min(2, len(claims))).copy()
    if not anomalies.empty:
        anomalies["claim_id"] = anomalies["claim_id"] + "-DUP"
        anomalies["claimed_amount_usd"] = -anomalies["claimed_amount_usd"]
        anomalies["anomaly_reason"] = "duplicate_fixture_and_negative_amount"
        anomalies.to_csv(output_dir / "claims_raw_anomalies.csv", index=False)

    tables = {"customers": customers, "vehicles": vehicles, "policies": policies, "claims": claims}
    for name, frame in tables.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)
    manifest = {
        "profile": profile,
        "seed": int(config["seed"]),
        "counts": {key: len(value) for key, value in tables.items()},
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest["counts"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate deterministic InsureIQ synthetic fixtures"
    )
    parser.add_argument("--profile", choices=("smoke", "full"), default="smoke")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/synthetic"))
    args = parser.parse_args()
    config = args.config or Path("configs") / f"{args.profile}.yml"
    counts = generate(args.profile, config, args.output)
    print(f"Datos sintéticos generados ({args.profile}): {counts}")


if __name__ == "__main__":
    main()
