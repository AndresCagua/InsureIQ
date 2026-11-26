"""Fraud benchmark training utilities with explicit data availability checks."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


class FraudDataError(ValueError):
    """Raised when a verified fraud benchmark cannot be used."""


def load_benchmark(
    path: Path, target: str = "fraud"
) -> tuple[pd.DataFrame, pd.Series]:
    """Load a benchmark and fail clearly when its target is unavailable."""
    if not path.exists():
        raise FraudDataError(
            f"No existe el benchmark de fraude: {path}. "
            "Completa data/sources.yml y descarga manualmente."
        )
    frame = pd.read_csv(path)
    if target not in frame.columns:
        raise FraudDataError(f"Falta la columna objetivo '{target}' en {path}")
    target_values = frame[target]
    features = frame.drop(columns=[target])
    if target_values.nunique() < 2:
        raise FraudDataError("El benchmark debe contener al menos dos clases de fraude")
    return features, target_values


def train_baseline(
    features: pd.DataFrame, target: pd.Series
) -> tuple[Pipeline, dict[str, float]]:
    """Train a logistic baseline using preprocessing fit only on the train split."""
    numeric = features.select_dtypes(include="number").columns.tolist()
    categorical = [column for column in features.columns if column not in numeric]
    transformers = []
    if numeric:
        transformers.append(
            (
                "numeric",
                Pipeline(
                    [("imputer", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
                ),
                numeric,
            )
        )
    if categorical:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            )
        )
    if not transformers:
        raise FraudDataError("El benchmark no contiene features utilizables")
    preprocessor = ColumnTransformer(transformers)
    model = Pipeline(
        [
            ("preprocess", preprocessor),
            (
                "classifier",
                LogisticRegression(max_iter=500, class_weight="balanced", random_state=42),
            ),
        ]
    )
    x_train, x_test, y_train, y_test = train_test_split(
        features, target, test_size=0.25, random_state=42, stratify=target
    )
    model.fit(x_train, y_train)
    probabilities = model.predict_proba(x_test)[:, 1]
    metrics = {
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "average_precision": float(average_precision_score(y_test, probabilities)),
        "test_rows": float(len(y_test)),
    }
    return model, metrics


def train_from_path(path: Path, output_path: Path, target: str = "fraud") -> dict[str, float]:
    """Train and write metrics plus intended-use limitations."""
    features, labels = load_benchmark(path, target)
    _, metrics = train_baseline(features, labels)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "metrics": metrics,
                "target": target,
                "recommendation": "MANUAL_REVIEW or STANDARD_REVIEW; never auto-deny",
                "limitations": (
                    "Benchmark results are not Ecuadorian validation and do not "
                    "prove fraud causally."
                ),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return metrics
