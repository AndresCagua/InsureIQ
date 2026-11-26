import pandas as pd

from insureiq.fraud import train_baseline


def test_fraud_baseline_fits_preprocessing_inside_pipeline() -> None:
    features = pd.DataFrame(
        {
            "amount": [10, 12, 15, 20, 50, 55, 60, 70, 80, 90, 100, 110],
            "channel": ["web", "web", "agent", "agent"] * 3,
        }
    )
    target = pd.Series([0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1], name="fraud")
    _, metrics = train_baseline(features, target)
    assert set(metrics) == {"roc_auc", "average_precision", "test_rows"}
    assert metrics["test_rows"] == 3.0
