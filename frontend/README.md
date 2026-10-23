# SoilCast — Soil Moisture Forecasting Dashboard

Frontend-first Next.js dashboard for soil-moisture forecasting at 50 cm depth (`SM_50cm`), with a 24-hour horizon and 15-minute interval.

## Run

```bash
npm install
npm run dev
```

Open http://localhost:3000.

## Backend integration

Copy `.env.example` to `.env.local` and set `NEXT_PUBLIC_API_BASE_URL` to your FastAPI base URL, then restart Next.js. The frontend tries `GET /api/health` and `GET /api/forecast`. The UI falls back to clearly labelled illustrative demo data if no API URL is configured or the API is unavailable.

### Suggested forecast response

```json
{
  "target": "SM_50cm",
  "horizon_hours": 24,
  "interval_minutes": 15,
  "generated_at": "2026-10-20T10:00:00+05:30",
  "observed": [{"timestamp":"2026-10-20T09:45:00+05:30","value":26.8}],
  "predictions": [{"timestamp":"2026-10-20T10:00:00+05:30","value":26.7}],
  "metrics": {"mae": null, "rmse": null, "r2": null},
  "baseline": {"name":"Persistence", "mae":null, "rmse":null, "r2":null}
}
```

`observed` should contain recent observations and `predictions` should contain 96 future points. Metrics must be actual held-out evaluation results; use `null` when unavailable. Adapt `lib/api.ts` if the backend contract differs.

## Pages
- Overview
- Forecast
- Data explorer
- Model evaluation
- Irrigation guidance

Demo values are illustrative only. The irrigation threshold is not validated agronomic advice. No hardware is controlled.
