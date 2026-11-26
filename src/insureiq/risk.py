"""Exposure-aware frequency, severity and pure-premium baselines."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.linear_model import GammaRegressor, PoissonRegressor
from sklearn.metrics import mean_absolute_error


class RiskDataError(ValueError):
    """Raised when risk inputs cannot support an exposure-aware model."""


def build_policy_training_frame(policy_path: Path, claim_path: Path) -> pd.DataFrame:
    """Aggregate claim rows to policy grain and keep exposure explicit."""
    policies = pd.read_csv(policy_path)
    claims = pd.read_csv(claim_path)
    required_policy = {"policy_id", "annual_premium_usd"}
    required_claim = {"policy_id", "claimed_amount_usd"}
    if not required_policy.issubset(policies.columns):
        raise RiskDataError("La tabla de pólizas no tiene las columnas requeridas")
    if not required_claim.issubset(claims.columns):
        raise RiskDataError("La tabla de siniestros no tiene las columnas requeridas")
    claim_agg = claims.groupby("policy_id").agg(
        claim_count=("claim_id", "count"),
        incurred_amount_usd=("claimed_amount_usd", "sum"),
    )
    frame = policies.join(claim_agg, on="policy_id").fillna(
        {"claim_count": 0, "incurred_amount_usd": 0}
    )
    frame["exposure_years"] = 1.0
    frame["severity_usd"] = frame["incurred_amount_usd"].div(frame["claim_count"].replace(0, pd.NA))
    return frame


def train_risk_baselines(frame: pd.DataFrame) -> dict[str, float]:
    """Fit Poisson frequency and Gamma severity baselines on policy-level data."""
    if len(frame) < 4 or frame["claim_count"].sum() < 2:
        raise RiskDataError("Se requieren pólizas y al menos dos siniestros para entrenar")
    features = frame[["annual_premium_usd"]]
    frequency = PoissonRegressor(alpha=0.1, max_iter=500)
    frequency.fit(features, frame["claim_count"], sample_weight=frame["exposure_years"])
    predicted_frequency = frequency.predict(features)
    claim_rows = frame[frame["claim_count"] > 0]
    severity = GammaRegressor(alpha=0.1, max_iter=500)
    severity.fit(claim_rows[["annual_premium_usd"]], claim_rows["severity_usd"])
    predicted_severity = severity.predict(claim_rows[["annual_premium_usd"]])
    pure_premium = predicted_frequency * severity.predict(features)
    return {
        "frequency_mae": float(mean_absolute_error(frame["claim_count"], predicted_frequency)),
        "severity_mae": float(
            mean_absolute_error(claim_rows["severity_usd"], predicted_severity)
        ),
        "portfolio_predicted_annual_loss_usd": float(pure_premium.sum()),
        "exposure_years": float(frame["exposure_years"].sum()),
    }


def train_from_paths(policy_path: Path, claim_path: Path, output_path: Path) -> dict[str, float]:
    """Train baselines and save metrics with their synthetic-data limitation."""
    frame = build_policy_training_frame(policy_path, claim_path)
    metrics = train_risk_baselines(frame)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "metrics": metrics,
                "exposure_convention": "one policy-year per synthetic policy row",
                "limitations": "Synthetic demonstration; not Ecuadorian actuarial validation.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return metrics
