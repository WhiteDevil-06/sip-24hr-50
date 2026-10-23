
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

// Set NEXT_PUBLIC_API_BASE_URL in .env.local when the backend is ready.
const base = (
  process.env.NEXT_PUBLIC_API_BASE_URL || ""
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

export function getApiConfigured(): boolean {
  return Boolean(base);
}
