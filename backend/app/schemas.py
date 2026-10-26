"""
Phase 6 — Pydantic schemas for /api/v1/predict request and response.
All validation matches the frozen API_CONTRACT.md specification exactly.
"""

from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, field_validator, model_validator

FEATURE_COLS = ["SM_50cm", "SM_5cm", "Temp_50cm", "Temp_5cm", "Precipitation"]
WINDOW_SIZE = 96
STEP_MINUTES = 15


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class PredictRequest(BaseModel):
    timestamps: List[str]
    features: dict[str, List[float]]

    @field_validator("timestamps")
    @classmethod
    def validate_timestamps(cls, v: List[str]) -> List[str]:
        if len(v) != WINDOW_SIZE:
            raise ValueError(
                f"timestamps must have exactly {WINDOW_SIZE} entries, got {len(v)}"
            )
        # Parse and check monotonic 15-min spacing
        parsed: List[datetime] = []
        for ts in v:
            try:
                parsed.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
            except ValueError:
                raise ValueError(f"Invalid ISO-8601 timestamp: {ts!r}")
        for i in range(1, len(parsed)):
            diff = (parsed[i] - parsed[i - 1]).total_seconds()
            if abs(diff - STEP_MINUTES * 60) > 1:  # 1-second tolerance
                raise ValueError(
                    f"Timestamps must be monotonically increasing by {STEP_MINUTES} minutes. "
                    f"Gap between index {i-1} and {i} is {diff:.0f} seconds."
                )
        return v

    @field_validator("features")
    @classmethod
    def validate_features(cls, v: dict) -> dict:
        missing = [c for c in FEATURE_COLS if c not in v]
        if missing:
            raise ValueError(f"Missing feature arrays: {missing}")
        for col in FEATURE_COLS:
            arr = v[col]
            if len(arr) != WINDOW_SIZE:
                raise ValueError(
                    f"Feature '{col}' must have {WINDOW_SIZE} values, got {len(arr)}"
                )
            import math
            for idx, val in enumerate(arr):
                if not math.isfinite(val):
                    raise ValueError(
                        f"Feature '{col}' contains non-finite value at index {idx}: {val}"
                    )
        return v


# ---------------------------------------------------------------------------
# Response sub-models
# ---------------------------------------------------------------------------

class IrrigationAdvisory(BaseModel):
    recommendation: str
    action_required: bool
    urgency: str
    current_value: float
    predicted_value: float
    optimal_range_min: float
    optimal_range_max: float
    wilting_point: float
    field_capacity: float
    explanation: str


class PredictResponse(BaseModel):
    status: str
    forecast_horizon_hours: int
    target_variable: str
    units: str
    input_window_end: str
    forecast_timestamp: str
    predicted_sm_50cm: float
    current_sm_50cm: float
    predicted_change_24h: float
    irrigation_advisory: IrrigationAdvisory


# ---------------------------------------------------------------------------
# Metrics response
# ---------------------------------------------------------------------------

class ModelMetrics(BaseModel):
    mae: float
    rmse: float
    r2: float


class MetricsResponse(BaseModel):
    test_dataset: str
    total_test_samples: int
    models: dict[str, ModelMetrics]


# ---------------------------------------------------------------------------
# Health response
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_version: str
    features_count: int
    device: str
    timestamp: str


# ---------------------------------------------------------------------------
# Frontend-friendly forecast endpoint response (Phase 8 integration)
# ---------------------------------------------------------------------------

class Observation(BaseModel):
    timestamp: str
    value: float


class ForecastApiResponse(BaseModel):
    target: str
    horizon_hours: int
    interval_minutes: int
    generated_at: str
    observed: List[Observation]
    predictions: List[Observation]
    metrics: dict | None = None
    baseline: dict | None = None
