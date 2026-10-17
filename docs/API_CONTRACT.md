# API Contract Specification (Preliminary)

> [!NOTE]
> This contract specification defines the planned interface between the FastAPI backend and Next.js frontend. It will be finalized and frozen during **Phase 5 (Model Handoff)** once model input shapes and features are approved by the Project Lead.

---

## 1. Endpoints Overview

| Method | Path | Description | Phase Available |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service health status and model load confirmation | Phase 6 |
| `POST` | `/api/v1/predict` | 24-hour soil moisture forecast prediction | Phase 6 |
| `GET` | `/api/v1/metrics` | Model performance benchmark metrics | Phase 6 |

---

## 2. Health Check Endpoint

### `GET /health`
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "lstm-v1",
  "timestamp": "2026-10-17T10:00:00Z"
}
```

---

## 3. Predict Endpoint

### `POST /api/v1/predict`
Accepts a sequence of the past $T$ observations (e.g., 96 steps of 15-minute data = 24 hours) and returns a 24-hour forward prediction curve for `SM_50cm`.

#### Request Schema:
```json
{
  "timestamps": ["2026-10-16T10:00:00Z", "..."],
  "features": {
    "SM_50cm": [0.24, 0.241, "..."],
    "rainfall": [0.0, 0.0, "..."],
    "temperature": [28.5, 28.7, "..."],
    "relative_humidity": [65.0, 64.5, "..."],
    "solar_radiation": [450.0, 460.0, "..."]
  }
}
```

#### Response Schema (`200 OK`):
```json
{
  "forecast_horizon_hours": 24,
  "target_variable": "SM_50cm",
  "unit": "m3/m3",
  "forecast_timestamps": ["2026-10-17T10:15:00Z", "... 96 steps ..."],
  "predictions": [0.239, 0.238, "..."],
  "irrigation_recommendation": {
    "recommended": false,
    "urgency": "none",
    "threshold_value": 0.18,
    "current_value": 0.24,
    "predicted_min": 0.235,
    "explanation": "Soil moisture at 50cm is projected to remain comfortably above the critical wilting point threshold of 0.18 m3/m3 for the next 24 hours."
  }
}
```

#### Error Responses:
- `400 Bad Request`: Input sequence length incorrect, feature ordering invalid, or non-finite values (`NaN`, `Inf`) detected.
- `422 Unprocessable Entity`: Schema validation failure.
- `503 Service Unavailable`: Model artifact failed to load or is not yet initialized.
