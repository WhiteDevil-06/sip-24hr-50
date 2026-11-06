export type Observation = {
  timestamp: string;
  value: number;
};

export type MetricSet = {
  mae?: number | null;
  rmse?: number | null;
  r2?: number | null;
};

export type ForecastResponse = {
  target: string;
  horizon_hours: number;
  interval_minutes: number;
  generated_at?: string;
  observed: Observation[];
  predictions: Observation[];
  metrics?: MetricSet | null;
  baseline?: ({ name?: string } & MetricSet) | null;
};

export type PredictPayload = {
  timestamps: string[];
  features: {
    SM_50cm: number[];
    SM_5cm: number[];
    Temp_50cm: number[];
    Temp_5cm: number[];
    Precipitation: number[];
  };
};

export type IrrigationAdvisory = {
  recommendation: string;
  action_required: boolean;
  urgency: string;
  current_value: number;
  predicted_value: number;
  optimal_range_min: number;
  optimal_range_max: number;
  wilting_point: number;
  field_capacity: number;
  explanation: string;
};

export type PredictResponse = {
  status: string;
  forecast_horizon_hours: number;
  target_variable: string;
  units: string;
  input_window_end: string;
  forecast_timestamp: string;
  predicted_sm_50cm: number;
  current_sm_50cm: number;
  predicted_change_24h: number;
  irrigation_advisory: IrrigationAdvisory;
};

const base = (
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
).replace(/\/+$/, "");

export async function fetchForecast(): Promise<ForecastResponse | null> {
  if (!base) return null;

  const response = await fetch(`${base}/api/forecast`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Forecast API returned ${response.status}`);
  }

  return response.json();
}

export async function checkApiHealth(): Promise<boolean> {
  if (!base) return false;

  try {
    const response = await fetch(`${base}/api/health`, {
      cache: "no-store",
    });

    return response.ok;
  } catch {
    return false;
  }
}

export async function runPrediction(payload: PredictPayload): Promise<PredictResponse | null> {
  if (!base) return null;

  const response = await fetch(`${base}/api/v1/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Inference API returned ${response.status}`);
  }

  return response.json();
}

export function getApiConfigured(): boolean {
  return Boolean(base);
}

// ---------------------------------------------------------------------------
// Historical Dataset Replay Types & Client Methods (Phase 2)
// ---------------------------------------------------------------------------

export type HistoricalSampleSummary = {
  id: string;
  title: string;
  badge: string;
  badgeColor: string;
  description: string;
  input_start: string;
  input_end: string;
  target_timestamp: string;
  current_sm_50cm: number;
  actual_future_sm_50cm: number;
  historical_rain_24h_mm: number;
};

export type HistoricalSampleDetail = HistoricalSampleSummary & {
  timestamps: string[];
  features: {
    SM_50cm: number[];
    SM_5cm: number[];
    Temp_50cm: number[];
    Temp_5cm: number[];
    Precipitation: number[];
  };
};

export async function fetchHistoricalSamples(): Promise<HistoricalSampleSummary[]> {
  if (!base) return [];

  const response = await fetch(`${base}/api/v1/historical-samples`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Historical samples API returned ${response.status}`);
  }

  return response.json();
}

export async function fetchHistoricalSample(sampleId: string): Promise<HistoricalSampleDetail | null> {
  if (!base) return null;

  const response = await fetch(`${base}/api/v1/historical-samples/${encodeURIComponent(sampleId)}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Historical sample '${sampleId}' returned ${response.status}`);
  }

  return response.json();
}

