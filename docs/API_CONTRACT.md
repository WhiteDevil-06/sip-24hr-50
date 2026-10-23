# API Contract Specification — Frozen Model Handoff

> [!IMPORTANT]
> **Status: FROZEN & APPROVED (Phase 5 Model Handoff — 2026-10-23)**
> This contract defines the strict production interface for Rahul's FastAPI service (`backend/`) and Ram Charan's Next.js web application (`frontend/`). No fields, feature orders, or units may be modified without Project Lead approval.

---

## 1. Endpoints Overview

| Method | Path | Description | Producer | Consumer |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service health status and model load confirmation | Backend (Rahul) | Frontend (Ram Charan) |
| `POST` | `/api/v1/predict` | 24-hour soil moisture forecast prediction | Backend (Rahul) | Frontend (Ram Charan) |
| `GET` | `/api/v1/metrics` | Model performance benchmark metrics | Backend (Rahul) | Frontend (Ram Charan) |

---

## 2. Health Check Endpoint

### `GET /health`
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_version": "SoilMoistureLSTM-v1",
  "features_count": 5,
  "device": "cpu",
  "timestamp": "2026-10-23T16:00:00Z"
}
```

---

## 3. Predict Endpoint

### `POST /api/v1/predict`
Accepts a chronological sequence of the past 96 observations ($\Delta t = 15 \text{ min}$, exactly 24 hours of inputs) and returns the forecasted `SM_50cm` value 24 hours ahead ($t + 96$).

#### Request Schema (`application/json`):
```json
{
  "timestamps": [
    "2026-10-22T10:00:00Z",
    "... exactly 96 ISO-8601 timestamps monotonically increasing by 15 mins ...",
    "2026-10-23T09:45:00Z"
  ],
  "features": {
    "SM_50cm": [15.2, 15.22, "... 96 float values (% VWC) ..."],
    "SM_5cm": [17.8, 17.85, "... 96 float values (% VWC) ..."],
    "Temp_50cm": [25.1, 25.12, "... 96 float values (°C) ..."],
    "Temp_5cm": [24.8, 24.84, "... 96 float values (°C) ..."],
    "Precipitation": [0.0, 0.0, "... 96 float values (mm/15min) ..."]
  }
}
```

#### Response Schema (`200 OK`):
```json
{
  "status": "success",
  "forecast_horizon_hours": 24,
  "target_variable": "SM_50cm",
  "units": "% Volumetric Water Content (VWC)",
  "input_window_end": "2026-10-23T09:45:00Z",
  "forecast_timestamp": "2026-10-24T09:45:00Z",
  "predicted_sm_50cm": 15.48,
  "current_sm_50cm": 15.20,
  "predicted_change_24h": 0.28,
  "irrigation_advisory": {
    "recommendation": "OPTIMAL_MOISTURE",
    "action_required": false,
    "urgency": "none",
    "current_value": 15.20,
    "predicted_value": 15.48,
    "optimal_range_min": 18.0,
    "optimal_range_max": 28.0,
    "wilting_point": 10.0,
    "field_capacity": 35.0,
    "explanation": "Soil moisture at 50 cm root zone is projected to remain stable at 15.48% VWC over the next 24 hours. No immediate irrigation required."
  }
}
```

#### Error Handling Responses:
- `400 Bad Request`: Input sequence length $\ne 96$, missing feature arrays, or non-finite numbers (`NaN`, `Inf`).
- `422 Unprocessable Entity`: Timestamps are not monotonically increasing by 15-minute intervals.
- `503 Service Unavailable`: Model weights (`models/best_model.pt`) or scalers failed to initialize at startup.

---

## 4. Metrics Endpoint

### `GET /api/v1/metrics`
Returns verified empirical benchmark metrics across test evaluation:

#### Response Schema (`200 OK`):
```json
{
  "test_dataset": "Held-Out Unseen Test Split (Jan 1, 2024 – Jun 30, 2025)",
  "total_test_samples": 52014,
  "models": {
    "persistence_baseline": {
      "mae": 0.6949,
      "rmse": 1.4206,
      "r2": 0.8303
    },
    "univariate_lstm": {
      "mae": 0.6639,
      "rmse": 1.2772,
      "r2": 0.8628
    },
    "multivariate_lstm_champion": {
      "mae": 0.7271,
      "rmse": 1.2798,
      "r2": 0.8623
    }
  }
}
```
