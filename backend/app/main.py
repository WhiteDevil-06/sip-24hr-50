"""
Phase 6 — FastAPI application entry point.

Endpoints (per frozen API_CONTRACT.md):
  GET  /health
  GET  /api/v1/metrics
  POST /api/v1/predict
  GET  /api/forecast          ← Phase 8 frontend-friendly wrapper
  GET  /api/health            ← Phase 8 frontend health alias
"""

import math
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

import numpy as np
import torch
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.inference import (
    build_irrigation_advisory,
    inverse_scale_target,
    scale_input,
)
from app.model_loader import (
    get_model,
    get_model_meta,
    get_scaler_meta,
    is_loaded,
    load_artifacts,
    load_error,
)
from app.schemas import (
    ForecastApiResponse,
    HealthResponse,
    IrrigationAdvisory,
    MetricsResponse,
    Observation,
    PredictRequest,
    PredictResponse,
)

# ---------------------------------------------------------------------------
# App + CORS
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model artifacts once at startup."""
    load_artifacts()
    yield


app = FastAPI(
    title="SoilCast — Soil Moisture Forecast API",
    version="1.0.0",
    description="FastAPI inference service for the LSTM-based 24-hour soil moisture forecast.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Phase 8: tighten to frontend origin in production
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)




# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    """Service health status and model load confirmation."""
    loaded = is_loaded()
    err = load_error()
    meta = get_model_meta() if loaded else {}
    return HealthResponse(
        status="healthy" if loaded else "degraded",
        model_loaded=loaded,
        model_version=meta.get("model_architecture", "SoilMoistureLSTM") + "-v1",
        features_count=len(meta.get("input_features", [])),
        device="cpu",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


# Phase 8 alias consumed by frontend lib/api.ts
@app.get("/api/health", response_model=HealthResponse, tags=["health"])
def api_health() -> HealthResponse:
    return health()


# ---------------------------------------------------------------------------
# Predict
# ---------------------------------------------------------------------------
@app.post("/api/v1/predict", response_model=PredictResponse, tags=["predict"])
def predict(body: PredictRequest) -> PredictResponse:
    """
    Accept 96-step input sequence and return 24-hour soil moisture forecast.
    """
    if not is_loaded():
        raise HTTPException(
            status_code=503,
            detail=f"Model not initialized. Startup error: {load_error()}",
        )

    scaler = get_scaler_meta()
    model_meta = get_model_meta()
    model = get_model()

    # Scale inputs → tensor
    scaled = scale_input(body.features, scaler)           # (1, 96, 5)
    x = torch.from_numpy(scaled)                          # float32 tensor

    with torch.no_grad():
        raw_pred = model(x).item()                        # scalar in scaled space

    # Back-transform to physical units
    pred_sm = inverse_scale_target(raw_pred, scaler)

    # Current SM is the last observed SM_50cm
    current_sm = body.features["SM_50cm"][-1]

    # Derive forecast timestamp
    last_ts = body.timestamps[-1]
    last_dt = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
    forecast_dt = last_dt + timedelta(hours=24)

    advisory = build_irrigation_advisory(current_sm, pred_sm, model_meta)

    return PredictResponse(
        status="success",
        forecast_horizon_hours=24,
        target_variable="SM_50cm",
        units="% Volumetric Water Content (VWC)",
        input_window_end=last_ts,
        forecast_timestamp=forecast_dt.isoformat(),
        predicted_sm_50cm=round(pred_sm, 6),
        current_sm_50cm=round(current_sm, 6),
        predicted_change_24h=round(pred_sm - current_sm, 6),
        irrigation_advisory=IrrigationAdvisory(**advisory),
    )


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
@app.get("/api/v1/metrics", response_model=MetricsResponse, tags=["metrics"])
def metrics() -> MetricsResponse:
    """Return verified empirical benchmark metrics from Phase 5 evaluation."""
    return MetricsResponse(
        test_dataset="Held-Out Unseen Test Split (Jan 1, 2024 – Jun 30, 2025)",
        total_test_samples=52014,
        models={
            "persistence_baseline": {"mae": 0.6949, "rmse": 1.4206, "r2": 0.8303},
            "univariate_lstm": {"mae": 0.6639, "rmse": 1.2772, "r2": 0.8628},
            "multivariate_lstm_champion": {"mae": 0.7271, "rmse": 1.2798, "r2": 0.8623},
        },
    )


# ---------------------------------------------------------------------------
# Phase 8: /api/forecast — frontend-friendly endpoint consumed by lib/api.ts
# ---------------------------------------------------------------------------
@app.get("/api/forecast", response_model=ForecastApiResponse, tags=["forecast"])
def forecast() -> ForecastApiResponse:
    """
    Returns a ready-to-render payload for the Next.js dashboard.
    Uses the last 96 15-min slots ending at 'now' as synthetic observed data,
    then runs the model to produce a 24-hour single-step prediction.
    The observed sequence is synthesised from a realistic steady value so the
    endpoint works without live sensor data being posted; in real deployment
    this should be replaced with a database or data-stream lookup.
    """
    if not is_loaded():
        raise HTTPException(status_code=503, detail="Model not ready")

    scaler = get_scaler_meta()
    model_meta = get_model_meta()
    model_metrics = get_model_meta().get("test_metrics", {})
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)

    # Build 96-step synthetic observed sequence ending at 'now'
    # Use a realistic mid-range SM_50cm value as a stable demo signal
    SM_DEMO = 22.5
    SM5_DEMO = 24.0
    T50_DEMO = 26.0
    T5_DEMO = 25.5
    PREC_DEMO = 0.0

    observed_timestamps = [
        (now - timedelta(minutes=15 * (95 - i))).isoformat() for i in range(96)
    ]
    raw_features = {
        "SM_50cm": [SM_DEMO] * 96,
        "SM_5cm": [SM5_DEMO] * 96,
        "Temp_50cm": [T50_DEMO] * 96,
        "Temp_5cm": [T5_DEMO] * 96,
        "Precipitation": [PREC_DEMO] * 96,
    }

    model = get_model()
    scaled = scale_input(raw_features, scaler)
    x = torch.from_numpy(scaled)
    with torch.no_grad():
        raw_pred = model(x).item()

    pred_sm = inverse_scale_target(raw_pred, scaler)
    forecast_ts = now + timedelta(hours=24)

    observed = [
        Observation(timestamp=ts, value=SM_DEMO)
        for ts in observed_timestamps
    ]
    predictions = [
        Observation(timestamp=forecast_ts.isoformat(), value=round(pred_sm, 4))
    ]

    return ForecastApiResponse(
        target="SM_50cm",
        horizon_hours=24,
        interval_minutes=15,
        generated_at=now.isoformat(),
        observed=observed,
        predictions=predictions,
        metrics={
            "mae": model_metrics.get("mae"),
            "rmse": model_metrics.get("rmse"),
            "r2": model_metrics.get("r2"),
        },
        baseline={
            "name": "Persistence baseline",
            "mae": 0.6949,
            "rmse": 1.4206,
            "r2": 0.8303,
        },
    )
