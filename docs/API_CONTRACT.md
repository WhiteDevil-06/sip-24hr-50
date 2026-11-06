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
| `GET` | `/api/v1/historical-samples` | List of curated historical test samples from 2024 test split | Backend (Rahul) | Frontend (Ram Charan) |
| `GET` | `/api/v1/historical-samples/{sample_id}` | Full 96-step sequence for a specific historical sample | Backend (Rahul) | Frontend (Ram Charan) |
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

---

## 5. Historical Dataset Replay Endpoints

These endpoints allow the client to inspect and replay real field observations from the held-out test split (2024) without data leakage.

### `GET /api/v1/historical-samples`
Returns summary metadata for all curated test samples.

#### Response Schema (`200 OK`):
```json
[
  {
    "id": "HIST-001-DROUGHT",
    "title": "Summer Drought Water Stress (May 2024)",
    "badge": "Water Stress",
    "badgeColor": "bg-amber-100 text-amber-800 border-amber-300",
    "description": "Pre-monsoon summer dry period with high thermal load (33°C). Root moisture is depleted (12.1%), requiring irrigation.",
    "input_start": "2024-05-06 16:30:00",
    "input_end": "2024-05-07 16:15:00",
    "target_timestamp": "2024-05-08T16:15:00",
    "current_sm_50cm": 12.1,
    "actual_future_sm_50cm": 13.5,
    "historical_rain_24h_mm": 0.0
  }
]
```

### `GET /api/v1/historical-samples/{sample_id}`
Returns the full 96-step sequence (5 features) for inference replay.

#### Response Schema (`200 OK`):
Includes all summary fields above plus:
* `timestamps`: Array of 96 ISO-8601 strings.
* `features`: Dictionary of 5 feature arrays (`SM_50cm`, `SM_5cm`, `Temp_50cm`, `Temp_5cm`, `Precipitation`), each containing exactly 96 float values in original physical units.

> [!NOTE]
> The evaluation ground-truth target `actual_future_sm_50cm` is strictly excluded from `features` and is provided for retrospective error calculation only (`|y - ŷ|`).

---

## 6. Agronomic Decision Logic & Thresholds

Both backend (`backend/app/main.py`) and frontend (`frontend/app/page.tsx`) adhere to the following unified decision criteria for root-zone moisture at 50 cm depth (`SM_50cm`):

| Moisture Range | Recommendation | Action Required | Urgency | Agronomic Meaning |
| :--- | :--- | :--- | :--- | :--- |
| $< 10.0\%$ VWC | `CRITICAL_DEFICIT` | `true` | `emergency` | Below Permanent Wilting Point (PWP). Severe crop stress. |
| $10.0\% - 18.0\%$ VWC | `DEFICIT_ALERT` | `true` | `high` | Management Allowed Depletion (MAD). Schedule irrigation within 24h. |
| $18.0\% - 35.0\%$ VWC | `OPTIMAL_MOISTURE` | `false` | `none` | Optimal crop growth zone. Transpiration and aeration balanced. |
| $> 35.0\%$ VWC | `EXCESS_MOISTURE` | `false` | `none` | Field capacity exceeded. Gravitational drainage; risk of hypoxia. |

