import pandas as pd

from insureiq.risk import train_risk_baselines


def test_risk_baselines_return_exposure_aware_metrics() -> None:
    frame = pd.DataFrame(
        {
            "annual_premium_usd": [300, 400, 500, 700, 900, 1200],
            "claim_count": [0, 1, 0, 2, 1, 2],
            "incurred_amount_usd": [0, 1000, 0, 2200, 800, 3000],
            "exposure_years": [1.0] * 6,
            "severity_usd": [pd.NA, 1000, pd.NA, 1100, 800, 1500],
        }
    )
    metrics = train_risk_baselines(frame)
    assert metrics["exposure_years"] == 6.0
    assert metrics["frequency_mae"] >= 0
    assert metrics["severity_mae"] >= 0
