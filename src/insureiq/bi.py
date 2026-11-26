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
    fraud_report = Path("reports/fraud_metrics.json")
    if fraud_report.exists():
        report = json.loads(fraud_report.read_text(encoding="utf-8"))
        metrics = report.get("metrics", {})
        ml_frame = pd.DataFrame(
            [
                {
                    "model": "fraud-baseline-public",
                    "task": "fraud_review_recommendation",
                    "metric": metric,
                    "value": value,
                    "is_ml": True,
                    "benchmark": "Zenodo 13381118",
                    "recommendation_policy": "MANUAL_REVIEW or STANDARD_REVIEW",
                }
                for metric, value in metrics.items()
            ]
        )
        ml_frame.to_csv(output_dir / "ml_fraud_metrics.csv", index=False)
        exported["ml_fraud_metrics.csv"] = len(ml_frame)
        benchmark_path = processed_dir / "public_vehicle_fraud_benchmark.csv"
        artifact_path = Path("reports/fraud_model.joblib")
        if benchmark_path.exists() and artifact_path.exists():
            import joblib

            benchmark = pd.read_csv(benchmark_path)
            model = joblib.load(artifact_path)
            feature_columns = report.get("feature_columns", [
                column for column in benchmark.columns if column != "fraud"
            ])
            probabilities = model.predict_proba(
                benchmark.drop(columns=["fraud"]).reindex(columns=feature_columns)
            )[:, 1]
            scored = benchmark[[
                column
                for column in [
                    "policy_number",
                    "total_claim_amount",
                    "incident_severity",
                    "incident_type",
                    "fraud",
                ]
                if column in benchmark.columns
            ]].copy()
            scored["fraud_probability"] = probabilities
            scored["recommendation"] = scored["fraud_probability"].map(
                lambda value: "MANUAL_REVIEW" if value >= 0.5 else "STANDARD_REVIEW"
            )
            queue = scored[scored["recommendation"] == "MANUAL_REVIEW"].sort_values(
                "fraud_probability", ascending=False
            )
            queue.to_csv(output_dir / "fraud_review_queue.csv", index=False)
            exported["fraud_review_queue.csv"] = len(queue)
            ml_frame = pd.concat(
                [
                    ml_frame,
                    pd.DataFrame(
                        [
                            {
                                "model": "fraud-baseline-public",
                                "task": "fraud_review_recommendation",
                                "metric": "manual_review_count",
                                "value": len(queue),
                                "is_ml": True,
                                "benchmark": "Zenodo 13381118",
                                "recommendation_policy": "threshold >= 0.5",
                            },
                            {
                                "model": "fraud-baseline-public",
                                "task": "fraud_review_recommendation",
                                "metric": "manual_review_rate",
                                "value": len(queue) / len(scored),
                                "is_ml": True,
                                "benchmark": "Zenodo 13381118",
                                "recommendation_policy": "threshold >= 0.5",
                            },
                        ]
                    ),
                ],
                ignore_index=True,
            )
            ml_frame.to_csv(output_dir / "ml_fraud_metrics.csv", index=False)
    (output_dir / "manifest.json").write_text(
        json.dumps({"exports": exported, "fixture": "golden_kpis.json"}, indent=2),
        encoding="utf-8",
    )
    return fixture
