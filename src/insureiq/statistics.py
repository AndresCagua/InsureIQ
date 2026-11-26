"""Reusable descriptive statistics for the InsureIQ notebooks."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def quality_report(data_dir: Path, output_path: Path) -> dict:
    """Create a reproducible quality and descriptive-statistics report."""
    tables = {}
    for path in sorted(data_dir.glob("*.csv")):
        frame = pd.read_csv(path)
        numeric = frame.select_dtypes("number")
        tables[path.stem] = {
            "rows": len(frame),
            "columns": len(frame.columns),
            "missing_values": int(frame.isna().sum().sum()),
            "duplicate_rows": int(frame.duplicated().sum()),
            "numeric_summary": (
                numeric.describe().round(4).to_dict() if not numeric.empty else {}
            ),
        }
    report = {"data_dir": str(data_dir), "tables": tables}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return report


def claims_summary(claims_path: Path) -> dict[str, float]:
    """Return transparent aggregate claim statistics without causal interpretation."""
    claims = pd.read_csv(claims_path)
    amounts = claims["claimed_amount_usd"]
    return {
        "claim_count": float(len(claims)),
        "total_claimed_amount_usd": float(amounts.sum()),
        "mean_claimed_amount_usd": float(amounts.mean()),
        "median_claimed_amount_usd": float(amounts.median()),
    }
