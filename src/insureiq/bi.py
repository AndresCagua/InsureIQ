"""Reproducible BI extracts and KPI fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def export_bi(processed_dir: Path, output_dir: Path) -> dict[str, object]:
    """Export stable CSV extracts and a golden KPI fixture."""
    output_dir.mkdir(parents=True, exist_ok=True)
    exported: dict[str, int] = {}
    for path in sorted(processed_dir.glob("*.csv")):
        frame = pd.read_csv(path)
        frame.to_csv(output_dir / path.name, index=False)
        exported[path.name] = len(frame)

    policies = pd.read_csv(processed_dir / "dim_policy.csv")
    claims = pd.read_csv(processed_dir / "fact_claim.csv")
    fixture = {
        "currency": "USD",
        "is_synthetic": True,
        "policy_count": int(len(policies)),
        "claim_count": int(len(claims)),
        "claimed_amount_usd": float(claims["claimed_amount_usd"].sum()),
        "written_premium_usd": float(policies["annual_premium_usd"].sum()),
        "source": "synthetic_ecuador_insurer",
    }
    (output_dir / "golden_kpis.json").write_text(
        json.dumps(fixture, indent=2), encoding="utf-8"
    )
    (output_dir / "manifest.json").write_text(
        json.dumps({"exports": exported, "fixture": "golden_kpis.json"}, indent=2),
        encoding="utf-8",
    )
    return fixture
