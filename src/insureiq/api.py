"""Versioned read-only inference API for the InsureIQ demo."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

app = FastAPI(title="InsureIQ API", version="0.1.0")
MODEL_REGISTRY = Path("reports/model_registry.json")
MODEL_ARTIFACT = Path("reports/fraud_model.joblib")


class FraudRequest(BaseModel):
    claim_id: str = Field(min_length=1, max_length=100)
    features: dict[str, float | str] = Field(default_factory=dict)


@app.middleware("http")
async def correlation_id(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = request.headers.get("X-Correlation-ID", str(uuid4()))
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    if not MODEL_REGISTRY.exists() or not MODEL_ARTIFACT.exists():
        raise HTTPException(status_code=503, detail="No hay modelo de fraude entrenado disponible")
    return {"status": "ready"}


@app.get("/api/v1/models")
def models() -> dict:
    if not MODEL_REGISTRY.exists():
        return {"models": []}
    return json.loads(MODEL_REGISTRY.read_text(encoding="utf-8"))


@app.post("/api/v1/fraud/predict")
def fraud_predict(request: FraudRequest) -> dict:
    if not MODEL_REGISTRY.exists() or not MODEL_ARTIFACT.exists():
        raise HTTPException(
            status_code=503,
            detail="El modelo de fraude no está disponible; ejecute make fraud-train.",
        )
    try:
        import joblib

        registry = json.loads(MODEL_REGISTRY.read_text(encoding="utf-8"))
        model_info = registry["models"][0]
        columns = model_info["feature_columns"]
        model = joblib.load(MODEL_ARTIFACT)
        features = pd.DataFrame([request.features]).reindex(columns=columns)
        probability = float(model.predict_proba(features)[0, 1])
    except (KeyError, OSError, ValueError, IndexError) as exc:
        raise HTTPException(status_code=503, detail=f"No se pudo cargar el modelo: {exc}") from exc
    return {
        "claim_id": request.claim_id,
        "fraud_probability": probability,
        "recommendation": "MANUAL_REVIEW" if probability >= 0.5 else "STANDARD_REVIEW",
        "model": model_info["name"],
        "disclaimer": "Resultado de benchmark público; requiere revisión humana.",
    }


@app.get("/api/v1/forecasts")
def forecasts() -> dict:
    path = Path("reports/forecast_metrics.json")
    if not path.exists():
        raise HTTPException(status_code=503, detail="No hay pronóstico generado")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/v1/metrics")
def metrics() -> dict[str, str]:
    return {"status": "demo", "data_policy": "synthetic_or_approved_public_only"}
