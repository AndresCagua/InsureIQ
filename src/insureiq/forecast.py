"""Transparent monthly forecasting baselines and rolling-origin backtesting."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


class ForecastDataError(ValueError):
    """Raised when a monthly series is not forecastable."""


def monthly_claim_series(claim_path: Path) -> pd.Series:
    """Aggregate claims to a complete monthly count series."""
    claims = pd.read_csv(claim_path, parse_dates=["loss_date"])
    if claims.empty:
        raise ForecastDataError("No hay siniestros para construir la serie")
    series = claims.set_index("loss_date")["claim_id"].resample("MS").count().astype(float)
    return series.asfreq("MS", fill_value=0.0)


def seasonal_naive_forecast(
    history: pd.Series, horizon: int, season_length: int = 12
) -> np.ndarray:
    """Forecast using the latest observed seasonal values."""
    if len(history) < season_length:
        raise ForecastDataError("Se requieren al menos 12 meses para naive estacional")
    return np.resize(history.iloc[-season_length:].to_numpy(), horizon).astype(float)


def rolling_origin_backtest(series: pd.Series, horizon: int = 1) -> dict[str, float]:
    """Evaluate a seasonal-naive baseline without random splitting."""
    if len(series) < 14:
        raise ForecastDataError("Se requieren al menos 14 meses para backtesting")
    actual = []
    predicted = []
    for end in range(12, len(series) - horizon + 1):
        history = series.iloc[:end]
        actual.extend(series.iloc[end : end + horizon].to_numpy())
        predicted.extend(seasonal_naive_forecast(history, horizon))
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "backtest_points": float(len(actual)),
        "interval_coverage_80": float(
            np.mean(
                (np.asarray(actual) >= 0)
                & (np.asarray(actual) <= np.asarray(predicted) * 2 + 1)
            )
        ),
    }


def forecast_from_path(claim_path: Path, output_path: Path) -> dict[str, float]:
    """Backtest the count baseline and save methodology metadata."""
    series = monthly_claim_series(claim_path)
    metrics = rolling_origin_backtest(series)
    output = {
        "metrics": metrics,
        "series_start": str(series.index.min().date()),
        "series_end": str(series.index.max().date()),
        "baseline": "seasonal_naive_12",
        "interval_method": (
            "illustrative non-negative baseline band; "
            "not a calibrated prediction interval"
        ),
        "limitations": "Synthetic history; no claim of real-world forecast validity.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return metrics
