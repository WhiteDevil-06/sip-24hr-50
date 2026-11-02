"""
Phase 8 — Integration tests.
Verifies that the frontend lib/api.ts interface contract matches what
the backend actually returns. Runs against the FastAPI TestClient.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402
from app.model_loader import is_loaded  # noqa: E402

client = TestClient(app)


class TestCORS:
    """Backend must return correct CORS headers for frontend requests."""

    def test_options_preflight(self):
        r = client.options(
            "/api/v1/predict",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        # FastAPI CORSMiddleware returns 200 for OPTIONS preflight
        assert r.status_code == 200
        assert "access-control-allow-origin" in r.headers

    def test_cors_header_on_get(self):
        r = client.get("/health", headers={"Origin": "http://localhost:3000"})
        assert "access-control-allow-origin" in r.headers


class TestForecastContractShape:
    """
    The frontend lib/api.ts fetchForecast() expects this shape:
      { target, horizon_hours, interval_minutes, generated_at, observed[], predictions[], metrics?, baseline? }
    """

    def test_forecast_shape(self):
        r = client.get("/api/forecast")
        if not is_loaded():
            assert r.status_code == 503
            return
        assert r.status_code == 200
        data = r.json()

        # Required top-level fields from ForecastApiResponse
        for field in ("target", "horizon_hours", "interval_minutes", "generated_at",
                      "observed", "predictions"):
            assert field in data, f"Missing field: {field}"

        assert data["target"] == "SM_50cm"
        assert data["horizon_hours"] == 24
        assert data["interval_minutes"] == 15

        # observed entries must have timestamp + value
        assert len(data["observed"]) > 0
        for obs in data["observed"]:
            assert "timestamp" in obs
            assert "value" in obs

        # predictions entries
        assert len(data["predictions"]) > 0
        for pred in data["predictions"]:
            assert "timestamp" in pred
            assert "value" in pred

    def test_health_alias_shape(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        data = r.json()
        for field in ("status", "model_loaded", "model_version", "features_count", "device", "timestamp"):
            assert field in data


class TestErrorHandling:
    """Graceful degradation checks."""

    def test_bad_json_returns_422(self):
        r = client.post(
            "/api/v1/predict",
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )
        assert r.status_code == 422

    def test_unknown_route_404(self):
        r = client.get("/nonexistent")
        assert r.status_code == 404
