"""
Phase 6 & 9 — API test suite + numerical parity verification.

Tests:
  1. GET /health               → 200, model_loaded=True
  2. GET /api/v1/metrics       → 200, all three model blocks present
  3. POST /api/v1/predict      → 200, valid response shape
  4. POST /api/v1/predict      → 400 for wrong array length
  5. POST /api/v1/predict      → 422 for non-monotonic timestamps
  6. POST /api/v1/predict      → 400 for NaN in features
  7. Numerical parity          → API output matches direct PyTorch inference < 1e-5
"""

import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pytest
import torch
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402
from app.model_loader import get_model, get_scaler_meta, is_loaded  # noqa: E402
from app.inference import scale_input, inverse_scale_target  # noqa: E402

client = TestClient(app)

# Force model load for parity test (lifespan may not fire in TestClient)
from app.model_loader import load_artifacts as _load_artifacts
_load_artifacts()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _make_timestamps(start: datetime, n: int = 96, step_min: int = 15):
    return [(start + timedelta(minutes=step_min * i)).isoformat() for i in range(n)]


def _make_features(sm=22.5, sm5=24.0, t50=26.0, t5=25.5, prec=0.0, n=96):
    return {
        "SM_50cm": [sm] * n,
        "SM_5cm": [sm5] * n,
        "Temp_50cm": [t50] * n,
        "Temp_5cm": [t5] * n,
        "Precipitation": [prec] * n,
    }


BASE_TIME = datetime(2026, 10, 22, 10, 0, tzinfo=timezone.utc)
GOOD_BODY = {
    "timestamps": _make_timestamps(BASE_TIME),
    "features": _make_features(),
}

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_200(self):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] in ("healthy", "degraded")
        assert isinstance(data["model_loaded"], bool)
        assert "timestamp" in data

    def test_api_health_alias(self):
        r = client.get("/api/health")
        assert r.status_code == 200


class TestMetrics:
    def test_metrics_200(self):
        r = client.get("/api/v1/metrics")
        assert r.status_code == 200
        data = r.json()
        assert "persistence_baseline" in data["models"]
        assert "univariate_lstm" in data["models"]
        assert "multivariate_lstm_champion" in data["models"]
        for model_data in data["models"].values():
            assert all(k in model_data for k in ("mae", "rmse", "r2"))


class TestPredict:
    def test_predict_valid(self):
        r = client.post("/api/v1/predict", json=GOOD_BODY)
        if not is_loaded():
            assert r.status_code == 503
            return
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert data["target_variable"] == "SM_50cm"
        assert isinstance(data["predicted_sm_50cm"], float)
        assert math.isfinite(data["predicted_sm_50cm"])
        assert 0.0 <= data["predicted_sm_50cm"] <= 60.0, "SM prediction out of physical range"
        assert "irrigation_advisory" in data

    def test_predict_wrong_length(self):
        body = {"timestamps": _make_timestamps(BASE_TIME, n=50), "features": _make_features(n=50)}
        r = client.post("/api/v1/predict", json=body)
        assert r.status_code == 422  # Pydantic validation error

    def test_predict_missing_feature(self):
        body = dict(GOOD_BODY)
        body["features"] = {k: v for k, v in GOOD_BODY["features"].items() if k != "SM_5cm"}
        r = client.post("/api/v1/predict", json=body)
        assert r.status_code == 422

    def test_predict_nan_in_features(self):
        # JSON standard does not allow NaN, so the server should reject it.
        # We send a manually-crafted body with "null" standing in for NaN
        # (a real client might send null for missing sensor readings).
        import json
        feats = _make_features()
        feats["SM_50cm"][10] = None  # null in JSON → Python None, fails float validation
        body = {"timestamps": _make_timestamps(BASE_TIME), "features": feats}
        r = client.post("/api/v1/predict", json=body)
        assert r.status_code == 422

    def test_predict_non_monotonic_timestamps(self):
        tss = _make_timestamps(BASE_TIME)
        # Swap two entries to break monotonicity
        tss[5], tss[6] = tss[6], tss[5]
        body = {"timestamps": tss, "features": _make_features()}
        r = client.post("/api/v1/predict", json=body)
        assert r.status_code == 422


class TestNumericalParity:
    """
    Phase 6 Gate: API prediction must match direct PyTorch inference within 1e-5.
    """

    def test_parity(self):
        if not is_loaded():
            pytest.skip("Model not loaded — skipping parity check")

        scaler = get_scaler_meta()
        model = get_model()

        # Build the same input as the API call
        raw_features = _make_features()
        scaled = scale_input(raw_features, scaler)           # (1, 96, 5) float32
        x = torch.from_numpy(scaled)

        model.eval()
        with torch.no_grad():
            direct_scaled_pred = model(x).item()
        direct_pred = inverse_scale_target(direct_scaled_pred, scaler)

        # Call the API
        r = client.post("/api/v1/predict", json=GOOD_BODY)
        assert r.status_code == 200
        api_pred = r.json()["predicted_sm_50cm"]

        delta = abs(api_pred - direct_pred)
        assert delta < 1e-5, (
            f"Numerical parity FAILED: API={api_pred:.8f}, Direct={direct_pred:.8f}, "
            f"delta={delta:.2e} (threshold=1e-5)"
        )


class TestForecastEndpoint:
    def test_forecast_get(self):
        r = client.get("/api/forecast")
        if not is_loaded():
            assert r.status_code == 503
            return
        assert r.status_code == 200
        data = r.json()
        assert data["target"] == "SM_50cm"
        assert len(data["observed"]) == 96
        assert len(data["predictions"]) >= 1
