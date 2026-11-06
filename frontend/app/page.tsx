"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Activity,
  AlertTriangle,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  Check,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CircleCheck,
  Clock3,
  CloudRain,
  Cpu,
  Database,
  Download,
  Droplets,
  FileChartColumn,
  FlaskConical,
  Gauge,
  HelpCircle,
  History,
  Info,
  Layers,
  LayoutDashboard,
  Menu,
  PanelLeftClose,
  PanelLeftOpen,
  RefreshCw,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Sprout,
  Sun,
  Thermometer,
  Waves,
  X,
  ChartNoAxesCombined,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  checkApiHealth,
  fetchHistoricalSample,
  fetchHistoricalSamples,
  getApiConfigured,
  runPrediction,
  type HistoricalSampleDetail,
  type HistoricalSampleSummary,
  type IrrigationAdvisory,
  type PredictPayload,
  type PredictResponse,
} from "../lib/api";

type Page =
  | "Simulation & Inference"
  | "Forecast Dynamics"
  | "Model Evaluation"
  | "Irrigation Guidance"
  | "Scenario Data";

type ScenarioKey = "drought" | "storm" | "drying" | "custom";

interface ScenarioConfig {
  id: ScenarioKey;
  title: string;
  badge: string;
  badgeColor: string;
  description: string;
  sm50: number;
  sm5: number;
  t50: number;
  t5: number;
  rain: number;
}

const PRESET_SCENARIOS: ScenarioConfig[] = [
  {
    id: "drought",
    title: "Summer Drought (Deficit Alert)",
    badge: "Water Stress",
    badgeColor: "bg-amber-100 text-amber-800 border-amber-300",
    description: "Extended dry spell, high surface evaporation (33°C), root moisture approaching wilting point.",
    sm50: 12.8,
    sm5: 8.4,
    t50: 29.5,
    t5: 33.2,
    rain: 0.0,
  },
  {
    id: "storm",
    title: "Monsoon Infiltration Front",
    badge: "Infiltration",
    badgeColor: "bg-blue-100 text-blue-800 border-blue-300",
    description: "Recent 24 mm storm event. Surface is saturated while water percolates downward into 50 cm root zone.",
    sm50: 19.5,
    sm5: 37.8,
    t50: 24.2,
    t5: 23.5,
    rain: 24.0,
  },
  {
    id: "drying",
    title: "Post-Irrigation Drying Cycle",
    badge: "Optimal Band",
    badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
    description: "Balanced root moisture following structured irrigation. Moderate solar desaturation.",
    sm50: 24.2,
    sm5: 26.0,
    t50: 25.5,
    t5: 26.8,
    rain: 0.0,
  },
  {
    id: "custom",
    title: "Interactive Parameter Tuner",
    badge: "User Defined",
    badgeColor: "bg-purple-100 text-purple-800 border-purple-300",
    description: "Freely adjust multi-depth moisture, temperatures, and precipitation sliders to test model inference.",
    sm50: 21.0,
    sm5: 22.5,
    t50: 26.0,
    t5: 27.0,
    rain: 5.0,
  },
];

const DEFAULT_HISTORICAL_SUMMARIES: HistoricalSampleSummary[] = [
  {
    id: "HIST-001-DROUGHT",
    title: "Summer Drought Water Stress (May 2024)",
    badge: "Water Stress",
    badgeColor: "bg-amber-100 text-amber-800 border-amber-300",
    description: "Pre-monsoon summer dry period with high thermal load (33°C). Root moisture is depleted (12.1%), requiring irrigation.",
    input_start: "2024-05-06 16:30:00",
    input_end: "2024-05-07 16:15:00",
    target_timestamp: "2024-05-08T16:15:00",
    current_sm_50cm: 12.1,
    actual_future_sm_50cm: 13.5,
    historical_rain_24h_mm: 0.0,
  },
  {
    id: "HIST-002-MONSOON",
    title: "Monsoon Infiltration Wavefront (July 2024)",
    badge: "Infiltration Surge",
    badgeColor: "bg-blue-100 text-blue-800 border-blue-300",
    description: "Major monsoon precipitation event (26.3 mm). Deep infiltration wavefront recharges 50 cm root zone.",
    input_start: "2024-07-15 03:00:00",
    input_end: "2024-07-16 02:45:00",
    target_timestamp: "2024-07-17T02:45:00",
    current_sm_50cm: 20.3,
    actual_future_sm_50cm: 21.7,
    historical_rain_24h_mm: 26.3,
  },
  {
    id: "HIST-003-STABLE",
    title: "Post-Monsoon Soil Equilibrium (Oct 2024)",
    badge: "Optimal Dynamic",
    badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
    description: "Stable moisture in the 18–20% optimal zone under moderate autumn temperatures (22–24°C). Zero rainfall.",
    input_start: "2024-10-25 15:45:00",
    input_end: "2024-10-26 15:30:00",
    target_timestamp: "2024-10-27T15:30:00",
    current_sm_50cm: 19.2,
    actual_future_sm_50cm: 18.9,
    historical_rain_24h_mm: 0.0,
  },
  {
    id: "HIST-004-WETTING",
    title: "Early Monsoon Soil Rehydration (July 2024)",
    badge: "Moisture Recovery",
    badgeColor: "bg-cyan-100 text-cyan-800 border-cyan-300",
    description: "First arrival of monsoon infiltration wetting front after initial dry spell. Root moisture begins rising.",
    input_start: "2024-07-04 12:45:00",
    input_end: "2024-07-05 12:30:00",
    target_timestamp: "2024-07-06T12:30:00",
    current_sm_50cm: 13.2,
    actual_future_sm_50cm: 16.4,
    historical_rain_24h_mm: 0.5,
  },
  {
    id: "HIST-005-WINTER",
    title: "Dry Winter Depletion Cycle (Feb 2024)",
    badge: "Slow Depletion",
    badgeColor: "bg-indigo-100 text-indigo-800 border-indigo-300",
    description: "Typical cool, dry post-harvest period. Gradual moisture drain from 15.5% toward deficit threshold.",
    input_start: "2024-02-12 08:30:00",
    input_end: "2024-02-13 08:15:00",
    target_timestamp: "2024-02-14T08:15:00",
    current_sm_50cm: 15.5,
    actual_future_sm_50cm: 14.6,
    historical_rain_24h_mm: 0.0,
  },
];

const NAV_ITEMS: { label: Page; icon: any; hint: string }[] = [
  {
    label: "Simulation & Inference",
    icon: Cpu,
    hint: "Simulate agricultural scenarios and run PyTorch neural inference.",
  },
  {
    label: "Forecast Dynamics",
    icon: ChartNoAxesCombined,
    hint: "Multi-depth sensor dynamics and 24-hour moisture projection trajectory.",
  },
  {
    label: "Model Evaluation",
    icon: FlaskConical,
    hint: "In-depth scientific comparison: Why LSTM outperforms Naïve Persistence.",
  },
  {
    label: "Irrigation Guidance",
    icon: Sprout,
    hint: "Threshold-based agronomic decision support and depletion management.",
  },
  {
    label: "Scenario Data",
    icon: Database,
    hint: "Inspect, paginate, filter, and export the 96-observation sequence.",
  },
];

// Helper: generate 96 timestamps ending at current time
function generateTimestamps(now: Date = new Date(), count: number = 96, stepMin: number = 15): string[] {
  const result: string[] = [];
  const start = new Date(now.getTime() - count * stepMin * 60 * 1000);
  for (let i = 0; i < count; i++) {
    result.push(new Date(start.getTime() + i * stepMin * 60 * 1000).toISOString());
  }
  return result;
}

// Synthesize physical 96-step time-series for a scenario
function synthesizeTimeSeries(
  sm50Base: number,
  sm5Base: number,
  t50Base: number,
  t5Base: number,
  rainEvent: number
): { timestamps: string[]; features: PredictPayload["features"] } {
  const count = 96;
  const timestamps = generateTimestamps(new Date(), count, 15);

  const sm50: number[] = [];
  const sm5: number[] = [];
  const t50: number[] = [];
  const t5: number[] = [];
  const prec: number[] = [];

  for (let i = 0; i < count; i++) {
    const fraction = i / count;
    // Diurnal temperature oscillation (warmer in day, cooler at night)
    const diurnal = Math.sin(fraction * Math.PI * 2 - 1.2);
    t50.push(Number((t50Base + diurnal * 1.5).toFixed(2)));
    t5.push(Number((t5Base + diurnal * 4.2).toFixed(2)));

    // Rain spike placed around step 60 (15h into past) if rainfall specified
    const isRainStep = rainEvent > 0 && i >= 55 && i <= 62;
    const rainVal = isRainStep ? Number((rainEvent / 8 + (i % 2 === 0 ? 0.3 : -0.2)).toFixed(2)) : 0.0;
    prec.push(Math.max(0, rainVal));

    // Surface moisture responds quickly to diurnal heat and rain
    let sm5Val = sm5Base - (1 - fraction) * 0.4 + diurnal * 0.8;
    if (rainEvent > 0 && i >= 58) {
      sm5Val += (rainEvent * 0.45) * Math.exp(-(count - i) * 0.04);
    }
    sm5.push(Number(Math.max(4.0, Math.min(50.0, sm5Val)).toFixed(2)));

    // Root moisture at 50 cm is more stable, damped, with slow gradual trend
    let sm50Val = sm50Base - (count - i) * 0.015;
    if (rainEvent > 0 && i >= 75) {
      // delayed infiltration arrival at 50 cm
      sm50Val += (rainEvent * 0.12) * ((i - 75) / 21);
    }
    sm50.push(Number(Math.max(6.0, Math.min(48.0, sm50Val)).toFixed(2)));
  }

  return {
    timestamps,
    features: {
      SM_50cm: sm50,
      SM_5cm: sm5,
      Temp_50cm: t50,
      Temp_5cm: t5,
      Precipitation: prec,
    },
  };
}

export default function Home() {
  const [page, setPage] = useState<Page>("Simulation & Inference");
  const [collapsed, setCollapsed] = useState<boolean>(false);
  const [mobileOpen, setMobileOpen] = useState<boolean>(false);
  const [apiConnected, setApiConnected] = useState<boolean>(true);
  const [busy, setBusy] = useState<boolean>(false);

  // Mode Selection: Synthetic Custom Simulation vs Historical Dataset Replay
  const [inputMode, setInputMode] = useState<"simulation" | "historical">("simulation");

  // Active scenario state (Simulation mode)
  const [selectedScenario, setSelectedScenario] = useState<ScenarioKey>("drought");
  const [customSM50, setCustomSM50] = useState<number>(18.5);
  const [customSM5, setCustomSM5] = useState<number>(20.0);
  const [customT50, setCustomT50] = useState<number>(26.0);
  const [customT5, setCustomT5] = useState<number>(28.0);
  const [customRain, setCustomRain] = useState<number>(10.0);

  // Historical replay state (Historical mode)
  const [historicalSamples, setHistoricalSamples] = useState<HistoricalSampleSummary[]>(DEFAULT_HISTORICAL_SUMMARIES);
  const [selectedHistoricalId, setSelectedHistoricalId] = useState<string>("HIST-001-DROUGHT");
  const [activeHistoricalDetail, setActiveHistoricalDetail] = useState<HistoricalSampleDetail | null>(null);

  // Inference state
  const [currentInput, setCurrentInput] = useState<PredictPayload | null>(null);
  const [prediction, setPrediction] = useState<PredictResponse | null>(null);
  const [evalTab, setEvalTab] = useState<"comparison" | "theory" | "metrics">("comparison");

  // Search, Filter & Pagination in Data Table
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [sortAsc, setSortAsc] = useState<boolean>(true);
  const [tablePage, setTablePage] = useState<number>(1);
  const PAGE_SIZE = 25;

  // Run simulation on synthetic scenario change or mount
  async function triggerSimulation(scenarioId: ScenarioKey) {
    setBusy(true);
    setActiveHistoricalDetail(null);
    try {
      let payloadInput: PredictPayload;
      if (scenarioId === "custom") {
        payloadInput = synthesizeTimeSeries(customSM50, customSM5, customT50, customT5, customRain);
      } else {
        const sc = PRESET_SCENARIOS.find((s) => s.id === scenarioId)!;
        payloadInput = synthesizeTimeSeries(sc.sm50, sc.sm5, sc.t50, sc.t5, sc.rain);
      }
      setCurrentInput(payloadInput);

      // Call FastAPI backend
      const res = await runPrediction(payloadInput);
      if (res) {
        setPrediction(res);
        setApiConnected(true);
      } else {
        // Fallback local calculation if backend disconnected (Threshold aligned with Phase 3 Contract)
        const currentSM = payloadInput.features.SM_50cm.at(-1)!;
        const delta = scenarioId === "storm" ? +1.8 : scenarioId === "drought" ? -0.9 : -0.2;
        const predVal = Number((currentSM + delta).toFixed(2));
        const rec =
          predVal < 10.0
            ? "CRITICAL_DEFICIT"
            : predVal < 18.0
            ? "DEFICIT_ALERT"
            : predVal > 35.0
            ? "EXCESS_MOISTURE"
            : "OPTIMAL_MOISTURE";
        const action = predVal < 18.0;
        const urgency = predVal < 10.0 ? "emergency" : predVal < 18.0 ? "high" : "none";

        setPrediction({
          status: "success",
          forecast_horizon_hours: 24,
          target_variable: "SM_50cm",
          units: "% Volumetric Water Content (VWC)",
          input_window_end: payloadInput.timestamps.at(-1)!,
          forecast_timestamp: new Date(Date.now() + 24 * 3600 * 1000).toISOString(),
          predicted_sm_50cm: predVal,
          current_sm_50cm: currentSM,
          predicted_change_24h: Number((predVal - currentSM).toFixed(2)),
          irrigation_advisory: {
            recommendation: rec,
            action_required: action,
            urgency,
            current_value: currentSM,
            predicted_value: predVal,
            optimal_range_min: 18.0,
            optimal_range_max: 35.0,
            wilting_point: 10.0,
            field_capacity: 35.0,
            explanation: `Simulated root moisture projected at ${predVal}% VWC over 24 hours. ${
              action
                ? "Depletion below 18% threshold; scheduling irrigation recommended."
                : "Moisture within optimal agronomic operating band."
            }`,
          },
        });
      }
    } catch {
      setApiConnected(false);
    } finally {
      setBusy(false);
    }
  }

  // Trigger historical replay with actual 2024 test data
  async function triggerHistoricalReplay(sampleId: string) {
    setBusy(true);
    setSelectedHistoricalId(sampleId);
    try {
      const detail = await fetchHistoricalSample(sampleId);
      if (detail) {
        setActiveHistoricalDetail(detail);
        const payloadInput: PredictPayload = {
          timestamps: detail.timestamps,
          features: detail.features,
        };
        setCurrentInput(payloadInput);

        const res = await runPrediction(payloadInput);
        if (res) {
          setPrediction(res);
          setApiConnected(true);
        }
      }
    } catch {
      setApiConnected(false);
    } finally {
      setBusy(false);
    }
  }

  // Switch between Custom Simulation and Historical Replay
  function handleModeChange(mode: "simulation" | "historical") {
    setInputMode(mode);
    if (mode === "simulation") {
      void triggerSimulation(selectedScenario);
    } else {
      void triggerHistoricalReplay(selectedHistoricalId);
    }
  }

  useEffect(() => {
    void triggerSimulation("drought");
    void checkApiHealth().then(setApiConnected);
    void fetchHistoricalSamples().then((samples) => {
      if (samples && samples.length > 0) {
        setHistoricalSamples(samples);
      }
    });
  }, []);

  // Compute chart trajectory combining observed 96 steps + 24h predictions
  const chartTrajectory = useMemo(() => {
    if (!currentInput) return [];
    const points = [];
    const sm50Arr = currentInput.features.SM_50cm;
    const sm5Arr = currentInput.features.SM_5cm;
    const lastSM50 = sm50Arr.at(-1) || 20.0;
    const targetPred = prediction ? prediction.predicted_sm_50cm : lastSM50 - 0.5;
    const actualTarget =
      inputMode === "historical" && activeHistoricalDetail
        ? activeHistoricalDetail.actual_future_sm_50cm
        : null;

    // Past 24h downsampled to hourly (every 4th 15-min point)
    for (let i = 0; i < 96; i += 4) {
      const hoursAgo = Math.round(((96 - i) * 15) / 60);
      points.push({
        label: `-${hoursAgo}h`,
        observed50: sm50Arr[i],
        observed5: sm5Arr[i],
        predictedLSTM: null,
        persistence: null,
        actualGroundTruth: null,
      });
    }

    // Current point (0h)
    points.push({
      label: "Now",
      observed50: lastSM50,
      observed5: sm5Arr.at(-1) || lastSM50,
      predictedLSTM: lastSM50,
      persistence: lastSM50,
      actualGroundTruth: null,
    });

    // Future 24h predictions (hourly trajectory from Now to +24h)
    for (let h = 1; h <= 24; h += 2) {
      const progress = h / 24;
      // LSTM smooth curvature
      const lstmVal = Number((lastSM50 + (targetPred - lastSM50) * Math.pow(progress, 0.85)).toFixed(2));
      // Naive Persistence remains rigidly flat at lastSM50
      const persVal = Number(lastSM50.toFixed(2));

      points.push({
        label: `+${h}h`,
        observed50: null,
        observed5: null,
        predictedLSTM: lstmVal,
        persistence: persVal,
        actualGroundTruth: h === 23 || h === 24 ? actualTarget : null,
      });
    }

    return points;
  }, [currentInput, prediction, inputMode, activeHistoricalDetail]);

  // Data table rows with search & pagination
  const allTableRows = useMemo(() => {
    if (!currentInput) return [];
    const rows = [];
    for (let i = 0; i < currentInput.timestamps.length; i++) {
      const rawTs = currentInput.timestamps[i];
      const parsed = new Date(rawTs);
      const timeStr = isNaN(parsed.getTime())
        ? rawTs.slice(11, 16) || rawTs
        : parsed.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });

      rows.push({
        step: i + 1,
        time: timeStr,
        fullTs: rawTs,
        sm50: currentInput.features.SM_50cm[i],
        sm5: currentInput.features.SM_5cm[i],
        temp50: currentInput.features.Temp_50cm[i],
        temp5: currentInput.features.Temp_5cm[i],
        rain: currentInput.features.Precipitation[i],
      });
    }
    const filtered = rows.filter((r) => r.time.includes(searchQuery) || r.fullTs.includes(searchQuery));
    return sortAsc ? filtered : filtered.reverse();
  }, [currentInput, searchQuery, sortAsc]);

  const totalPages = Math.max(1, Math.ceil(allTableRows.length / PAGE_SIZE));
  const paginatedRows = useMemo(() => {
    const start = (tablePage - 1) * PAGE_SIZE;
    return allTableRows.slice(start, start + PAGE_SIZE);
  }, [allTableRows, tablePage]);

  // Reset page to 1 on search or mode change
  useEffect(() => {
    setTablePage(1);
  }, [searchQuery, inputMode, selectedScenario, selectedHistoricalId]);

  function exportCsv() {
    if (!allTableRows.length) return;
    const header = "Step,Time,Full_Timestamp,SM_50cm_Percent,SM_5cm_Percent,Temp_50cm_C,Temp_5cm_C,Precipitation_mm\n";
    const body = allTableRows
      .map((r) => `${r.step},${r.time},${r.fullTs},${r.sm50},${r.sm5},${r.temp50},${r.temp5},${r.rain}`)
      .join("\n");
    const blob = new Blob([header + body], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `soilcast-${inputMode === "historical" ? selectedHistoricalId : selectedScenario}-96steps.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const activeNav = NAV_ITEMS.find((n) => n.label === page)!;

  return (
    <main className="app">
      {/* Collapsible Sidebar */}
      <aside className={`sidebar ${collapsed ? "collapsed" : ""} ${mobileOpen ? "open" : ""}`}>
        <div className="brand">
          <span className="brand-icon">
            <Droplets size={22} />
          </span>
          {!collapsed && (
            <div className="brand-text">
              <b>
                Soil<span>Cast</span>
              </b>
              <small>SOIL MOISTURE FORECASTING</small>
            </div>
          )}
          <button
            className="collapse-btn"
            onClick={() => setCollapsed(!collapsed)}
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
            aria-label="Toggle sidebar collapse"
          >
            {collapsed ? <PanelLeftOpen size={15} /> : <PanelLeftClose size={15} />}
          </button>
        </div>

        {!collapsed && <div className="nav-label">INFERENCE & SIMULATION</div>}

        <nav>
          {NAV_ITEMS.map(({ label, icon: Icon }) => (
            <button
              key={label}
              className={`nav-item ${page === label ? "active" : ""}`}
              onClick={() => {
                setPage(label);
                setMobileOpen(false);
              }}
              title={collapsed ? label : undefined}
            >
              <Icon size={18} />
              {!collapsed && <span>{label}</span>}
              {!collapsed && page === label && <i />}
            </button>
          ))}
        </nav>

        {!collapsed && (
          <div className="sidebar-bottom">
            <div className="side-note">
              <ShieldCheck size={18} />
              <b>Inference Engine</b>
              <p>PyTorch LSTM predicting root-zone soil moisture at 50 cm depth 24h ahead.</p>
            </div>
          </div>
        )}
      </aside>

      {mobileOpen && <button className="scrim" onClick={() => setMobileOpen(false)} aria-label="Close menu" />}

      {/* Main Content Area */}
      <section className={`main ${collapsed ? "sidebar-collapsed" : ""}`}>
        {/* Topbar */}
        <header className="topbar">
          <div className="crumb">
            <button className="open-mobile" onClick={() => setMobileOpen(true)}>
              <Menu size={18} />
            </button>
            <span>SoilCast</span>
            <i>/</i>
            <b>{page}</b>
          </div>

          <div className="top-actions">
            <span className={`api-pill ${apiConnected ? "connected" : "error"}`}>
              <i />
              {apiConnected ? "Inference Engine Active" : "Local Simulator"}
            </span>

            <button
              className="refresh"
              disabled={busy}
              onClick={() => {
                if (inputMode === "simulation") {
                  void triggerSimulation(selectedScenario);
                } else {
                  void triggerHistoricalReplay(selectedHistoricalId);
                }
              }}
              title="Re-run neural inference"
            >
              <RefreshCw size={13} className={busy ? "spin" : ""} />
              <span>Simulate</span>
            </button>
          </div>
        </header>

        {/* Viewport Content */}
        <div className="content">
          {/* Header Title */}
          <div className="page-title">
            <div>
              <div className="eyebrow">
                <i /> DEEP LEARNING SMART IRRIGATION
              </div>
              <h1>
                {page === "Simulation & Inference" ? (
                  <>
                    Simulate & Forecast.
                    <br />
                    <em>Root-Zone Precision.</em>
                  </>
                ) : (
                  page
                )}
              </h1>
              <p>{activeNav.hint}</p>
            </div>

            <div className="tags">
              <span>
                <Droplets size={13} /> Target: <b>SM_50cm</b>
              </span>
              <span>
                <Clock3 size={13} /> Forecast Horizon: <b>24 Hours Ahead</b>
              </span>
              <span>
                <Layers size={13} /> Model: <b>Multivariate LSTM</b>
              </span>
            </div>
          </div>

          {/* PAGE 1: SIMULATION & INFERENCE ENGINE */}
          {page === "Simulation & Inference" && (
            <>
              {/* Section 01: Mode Switcher & Scenarios */}
              <div className="section">
                <span>01</span>
                <h2>DATA INPUT MODE & SCENARIO SELECTION</h2>
                <i />
                <small>EVALUATE NEURAL INFERENCE</small>
              </div>

              {/* Mode Switcher Tabs */}
              <div className="mode-switcher">
                <button
                  className={`mode-btn ${inputMode === "simulation" ? "active" : ""}`}
                  onClick={() => handleModeChange("simulation")}
                >
                  <span className="mode-btn-icon">
                    <SlidersHorizontal size={18} />
                  </span>
                  <div className="mode-btn-content">
                    <strong>Mode A: Custom Simulation</strong>
                    <small>Generate physical scenarios or tweak moisture, temperature & rain sliders</small>
                  </div>
                </button>

                <button
                  className={`mode-btn ${inputMode === "historical" ? "active" : ""}`}
                  onClick={() => handleModeChange("historical")}
                >
                  <span className="mode-btn-icon">
                    <History size={18} />
                  </span>
                  <div className="mode-btn-content">
                    <strong>Mode B: Historical Dataset Replay</strong>
                    <small>Replay 5 real held-out test windows from 2024 test split with retrospective evaluation</small>
                  </div>
                </button>
              </div>

              {/* Mode A: Preset Simulation Scenarios */}
              {inputMode === "simulation" && (
                <>
                  <div className="scenario-grid">
                    {PRESET_SCENARIOS.map((sc) => {
                      const isActive = selectedScenario === sc.id;
                      return (
                        <button
                          key={sc.id}
                          className={`scenario-card ${isActive ? "active" : ""}`}
                          onClick={() => {
                            setSelectedScenario(sc.id);
                            void triggerSimulation(sc.id);
                          }}
                        >
                          <div className="scenario-card-head">
                            <span
                              className={`scenario-icon ${
                                sc.id === "drought"
                                  ? "bg-amber-100 text-amber-700"
                                  : sc.id === "storm"
                                  ? "bg-blue-100 text-blue-700"
                                  : sc.id === "drying"
                                  ? "bg-emerald-100 text-emerald-700"
                                  : "bg-purple-100 text-purple-700"
                              }`}
                            >
                              {sc.id === "drought" ? (
                                <Sun size={17} />
                              ) : sc.id === "storm" ? (
                                <CloudRain size={17} />
                              ) : sc.id === "drying" ? (
                                <Sprout size={17} />
                              ) : (
                                <SlidersHorizontal size={17} />
                              )}
                            </span>
                            <span className={`scenario-badge border ${sc.badgeColor}`}>{sc.badge}</span>
                          </div>
                          <strong>{sc.title}</strong>
                          <p>{sc.description}</p>
                        </button>
                      );
                    })}
                  </div>

                  {/* Custom Tuner Sliders if Custom selected */}
                  {selectedScenario === "custom" && (
                    <div className="tuner-grid">
                      <div className="tuner-control">
                        <label>
                          <span>Root Moisture (50 cm)</span>
                          <b>{customSM50}%</b>
                        </label>
                        <input
                          type="range"
                          min="8"
                          max="40"
                          step="0.5"
                          value={customSM50}
                          onChange={(e) => setCustomSM50(Number(e.target.value))}
                        />
                      </div>
                      <div className="tuner-control">
                        <label>
                          <span>Surface Moisture (5 cm)</span>
                          <b>{customSM5} %</b>
                        </label>
                        <input
                          type="range"
                          min="5"
                          max="45"
                          step="0.5"
                          value={customSM5}
                          onChange={(e) => setCustomSM5(Number(e.target.value))}
                        />
                      </div>
                      <div className="tuner-control">
                        <label>
                          <span>Soil Temperature (50 cm)</span>
                          <b>{customT50} °C</b>
                        </label>
                        <input
                          type="range"
                          min="18"
                          max="35"
                          step="0.5"
                          value={customT50}
                          onChange={(e) => setCustomT50(Number(e.target.value))}
                        />
                      </div>
                      <div className="tuner-control">
                        <label>
                          <span>Rainfall Event</span>
                          <b>{customRain} mm</b>
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="40"
                          step="1"
                          value={customRain}
                          onChange={(e) => setCustomRain(Number(e.target.value))}
                        />
                      </div>
                      <div style={{ gridColumn: "1 / -1", textAlign: "right", marginTop: "4px" }}>
                        <button className="primary-btn" onClick={() => triggerSimulation("custom")} disabled={busy}>
                          <Sparkles size={14} /> Run Neural Inference on Custom State
                        </button>
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* Mode B: Historical Test Samples */}
              {inputMode === "historical" && (
                <div className="scenario-grid five-col">
                  {historicalSamples.map((sample) => {
                    const isActive = selectedHistoricalId === sample.id;
                    return (
                      <button
                        key={sample.id}
                        className={`scenario-card ${isActive ? "active" : ""}`}
                        onClick={() => void triggerHistoricalReplay(sample.id)}
                      >
                        <div className="scenario-card-head">
                          <span className="scenario-icon bg-teal-100 text-teal-700">
                            <History size={17} />
                          </span>
                          <span className={`scenario-badge border ${sample.badgeColor}`}>{sample.badge}</span>
                        </div>
                        <strong>{sample.title}</strong>
                        <p>{sample.description}</p>
                        <div style={{ marginTop: "8px", fontSize: "10px", color: "#6e809c", display: "flex", justifyContent: "space-between", borderTop: "1px dashed #e2e8f1", paddingTop: "6px" }}>
                          <span>Start: <b>{sample.current_sm_50cm.toFixed(1)}%</b></span>
                          <span>Target: <b>{sample.actual_future_sm_50cm.toFixed(1)}%</b></span>
                          <span>Rain: <b>{sample.historical_rain_24h_mm.toFixed(1)}mm</b></span>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}

              {/* Key Indicators */}
              <div className="section">
                <span>02</span>
                <h2>INFERENCE OUTCOMES & ADVISORY</h2>
                <i />
                <small>24-HOUR ADVANCE FORECAST</small>
              </div>

              <div className="metrics">
                <div className="metric">
                  <div className="metric-top">
                    <span className="metric-icon mint">
                      <Droplets size={19} />
                    </span>
                    <small>SM_50cm</small>
                  </div>
                  <p>Current Observed Moisture</p>
                  <strong>
                    {prediction ? prediction.current_sm_50cm.toFixed(2) : "—"}
                    <i>% VWC</i>
                  </strong>
                </div>

                <div className="metric">
                  <div className="metric-top">
                    <span className="metric-icon blue">
                      <Waves size={19} />
                    </span>
                    <small>t + 24h</small>
                  </div>
                  <p>LSTM Forecast Horizon</p>
                  <strong>
                    {prediction ? prediction.predicted_sm_50cm.toFixed(2) : "—"}
                    <i>% VWC</i>
                  </strong>
                </div>

                <div className="metric">
                  <div className="metric-top">
                    <span className="metric-icon amber">
                      <Gauge size={19} />
                    </span>
                    <small>Change Δ</small>
                  </div>
                  <p>Projected 24h Shift</p>
                  <strong>
                    {prediction ? (
                      <>
                        {prediction.predicted_change_24h >= 0 ? "+" : ""}
                        {prediction.predicted_change_24h.toFixed(2)}
                      </>
                    ) : (
                      "—"
                    )}
                    <i> pp</i>
                  </strong>
                </div>

                <div className="metric">
                  <div className="metric-top">
                    <span className="metric-icon violet">
                      <Clock3 size={19} />
                    </span>
                    <small>Source Mode</small>
                  </div>
                  <p>{inputMode === "historical" ? "Real 2024 Test Set" : "Synthetic Simulation"}</p>
                  <strong>
                    96<i> steps</i>
                  </strong>
                </div>
              </div>

              {/* Mode B Retrospective Ground-Truth Comparison Banner */}
              {inputMode === "historical" && activeHistoricalDetail && prediction && (
                <div className="retrospective-banner">
                  <div className="retrospective-left">
                    <span className="panel-icon mint" style={{ width: "36px", height: "36px" }}>
                      <FlaskConical size={18} />
                    </span>
                    <div>
                      <strong>Ground-Truth Retrospective Evaluation ({activeHistoricalDetail.id})</strong>
                      <p>
                        Window: {activeHistoricalDetail.input_start} to {activeHistoricalDetail.input_end} · Target at {activeHistoricalDetail.target_timestamp}
                      </p>
                    </div>
                  </div>

                  <div className="retrospective-stats">
                    <div className="retrospective-stat">
                      <b>{activeHistoricalDetail.actual_future_sm_50cm.toFixed(2)}%</b>
                      <small>Actual Ground Truth (y)</small>
                    </div>
                    <div className="retrospective-stat">
                      <b>{prediction.predicted_sm_50cm.toFixed(2)}%</b>
                      <small>Model Forecast (ŷ)</small>
                    </div>
                    <div className="retrospective-stat">
                      <b>{Math.abs(activeHistoricalDetail.actual_future_sm_50cm - prediction.predicted_sm_50cm).toFixed(2)} pp</b>
                      <small>Absolute Error |y - ŷ|</small>
                    </div>
                  </div>
                </div>
              )}

              {/* Primary Trajectory Grid */}
              <div className="primary-grid">
                <article className="panel">
                  <div className="panel-head">
                    <div>
                      <div className="panel-title">
                        <span className="panel-icon mint">
                          <ChartNoAxesCombined size={17} />
                        </span>
                        <h2>Moisture Trajectory: Observed vs Forecast</h2>
                      </div>
                      <p>Past 24h observed sequence and +24h PyTorch LSTM prediction vs Naïve Persistence flatline</p>
                    </div>
                    <span className="chart-label">
                      <i /> PYTORCH INFERENCE
                    </span>
                  </div>

                  <div className="legend">
                    <span>
                      <i className="observed-dot" /> Past Observed (50 cm)
                    </span>
                    <span>
                      <i className="predicted-dot" /> LSTM Forecast (24h)
                    </span>
                    <span>
                      <i className="persistence-dot" /> Naïve Persistence Baseline
                    </span>
                    {inputMode === "historical" && (
                      <span>
                        <i style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#16a34a", display: "inline-block" }} /> Recorded Target (Ground Truth)
                      </span>
                    )}
                  </div>

                  <div className="chart h250">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={chartTrajectory} margin={{ top: 12, right: 12, left: -16, bottom: 0 }}>
                        <CartesianGrid stroke="#e8edf5" strokeDasharray="3 5" vertical={false} />
                        <XAxis
                          dataKey="label"
                          axisLine={false}
                          tickLine={false}
                          tick={{ fill: "#8292ab", fontSize: 10 }}
                          dy={8}
                        />
                        <YAxis
                          domain={["auto", "auto"]}
                          axisLine={false}
                          tickLine={false}
                          tick={{ fill: "#8292ab", fontSize: 10 }}
                        />
                        <Tooltip
                          content={({ active, payload, label }) => {
                            if (!active || !payload?.length) return null;
                            return (
                              <div className="tooltip">
                                <b>{label}</b>
                                {payload.map((p: any) => (
                                  <p key={p.dataKey}>
                                    <i style={{ background: p.color }} />
                                    {p.name}: <strong>{Number(p.value).toFixed(2)}%</strong>
                                  </p>
                                ))}
                              </div>
                            );
                          }}
                        />
                        <Line
                          dataKey="observed50"
                          name="Observed (50cm)"
                          stroke="#77889e"
                          strokeWidth={2.5}
                          dot={false}
                          connectNulls={false}
                        />
                        <Line
                          dataKey="predictedLSTM"
                          name="LSTM Forecast"
                          stroke="#24817a"
                          strokeWidth={3}
                          dot={false}
                          strokeDasharray="6 4"
                          connectNulls={false}
                        />
                        <Line
                          dataKey="persistence"
                          name="Naive Persistence"
                          stroke="#d97736"
                          strokeWidth={2}
                          dot={false}
                          strokeDasharray="3 3"
                          connectNulls={false}
                        />
                        {inputMode === "historical" && (
                          <Line
                            dataKey="actualGroundTruth"
                            name="Actual Ground Truth (24h)"
                            stroke="#16a34a"
                            strokeWidth={0}
                            dot={{ r: 6, fill: "#16a34a", stroke: "#ffffff", strokeWidth: 2 }}
                            connectNulls={false}
                          />
                        )}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="panel-foot">
                    <span>
                      Depth: <b>50 cm (Root Zone)</b>
                    </span>
                    <span>
                      Infiltration Model: <b>2-Layer PyTorch LSTM</b>
                    </span>
                    <span>
                      Sampling Cadence: <b>15 min (96 steps)</b>
                    </span>
                  </div>
                </article>

                {/* Irrigation Decision Card */}
                <article className="panel">
                  <div className="panel-title">
                    <span className="panel-icon amber">
                      <Sprout size={17} />
                    </span>
                    <h2>Irrigation Advisory & Decision Support</h2>
                  </div>
                  <p className="sub">Threshold-based agronomic guidance for 50 cm root zone</p>

                  <div className="soil-art">
                    <div className="sun" />
                    <div className="hill a" />
                    <div className="hill b" />
                    <div className="plant p1">
                      <i />
                      <b />
                    </div>
                    <div className="plant p2">
                      <i />
                      <b />
                    </div>
                    <div className="layer l1" />
                    <div className="layer l2" />
                    <div className="layer l3" />
                    <span className="soil-tag">
                      <Droplets size={11} /> Root Zone 50 cm
                    </span>
                  </div>

                  {prediction && (
                    <div
                      className={`advisory-card ${
                        prediction.irrigation_advisory.action_required ? "warn" : ""
                      }`}
                      style={{ marginTop: "14px" }}
                    >
                      <span className="advisory-icon">
                        {prediction.irrigation_advisory.action_required ? (
                          <AlertTriangle size={22} />
                        ) : (
                          <CircleCheck size={22} />
                        )}
                      </span>
                      <div className="advisory-body">
                        <small>{prediction.irrigation_advisory.urgency.toUpperCase()} PRIORITY</small>
                        <h2>
                          {prediction.irrigation_advisory.recommendation === "DEFICIT_ALERT"
                            ? "Irrigation Recommended"
                            : prediction.irrigation_advisory.recommendation === "CRITICAL_DEFICIT"
                            ? "Critical Water Deficit Alert"
                            : prediction.irrigation_advisory.recommendation === "EXCESS_MOISTURE"
                            ? "Excess Moisture / Drainage Safe"
                            : "Optimal Moisture Maintained"}
                        </h2>
                        <p>{prediction.irrigation_advisory.explanation}</p>
                      </div>
                    </div>
                  )}

                  {/* Standard Decision Bounds Legend */}
                  <div
                    style={{
                      marginTop: "14px",
                      display: "grid",
                      gridTemplateColumns: "repeat(4, 1fr)",
                      gap: "6px",
                      fontSize: "10px",
                      color: "#8291a7",
                      textAlign: "center",
                      borderTop: "1px solid #edf1f7",
                      paddingTop: "10px",
                    }}
                  >
                    <div>
                      <span style={{ display: "block", color: "#d9534f", fontWeight: 700 }}>&lt; 10.0%</span>
                      <span>Wilting Point</span>
                    </div>
                    <div>
                      <span style={{ display: "block", color: "#d97736", fontWeight: 700 }}>10.0% – 18.0%</span>
                      <span>Deficit Alert</span>
                    </div>
                    <div>
                      <span style={{ display: "block", color: "#24817a", fontWeight: 700 }}>18.0% – 35.0%</span>
                      <span>Optimal Zone</span>
                    </div>
                    <div>
                      <span style={{ display: "block", color: "#3d97e8", fontWeight: 700 }}>&gt; 35.0%</span>
                      <span>Field Capacity</span>
                    </div>
                  </div>
                </article>
              </div>
            </>
          )}

          {/* PAGE 2: FORECAST DYNAMICS */}
          {page === "Forecast Dynamics" && (
            <div style={{ display: "grid", gap: "16px" }}>
              <article className="panel">
                <div className="panel-head">
                  <div>
                    <div className="panel-title">
                      <span className="panel-icon blue">
                        <Layers size={18} />
                      </span>
                      <h2>Multi-Depth Moisture Gradient (5 cm vs 50 cm)</h2>
                    </div>
                    <p>Demonstrating vertical moisture percolation and thermal buffering through soil layers</p>
                  </div>
                </div>

                <div className="chart h280">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                      data={chartTrajectory.filter((p) => p.observed50 !== null)}
                      margin={{ top: 12, right: 12, left: -16, bottom: 0 }}
                    >
                      <defs>
                        <linearGradient id="colorSM5" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3d97e8" stopOpacity={0.25} />
                          <stop offset="95%" stopColor="#3d97e8" stopOpacity={0.0} />
                        </linearGradient>
                        <linearGradient id="colorSM50" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#24817a" stopOpacity={0.35} />
                          <stop offset="95%" stopColor="#24817a" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid stroke="#e8edf5" strokeDasharray="3 5" vertical={false} />
                      <XAxis dataKey="label" axisLine={false} tickLine={false} tick={{ fill: "#8292ab", fontSize: 10 }} dy={8} />
                      <YAxis axisLine={false} tickLine={false} tick={{ fill: "#8292ab", fontSize: 10 }} />
                      <Tooltip />
                      <Area type="monotone" dataKey="observed5" name="Surface (5cm)" stroke="#3d97e8" strokeWidth={2} fill="url(#colorSM5)" />
                      <Area type="monotone" dataKey="observed50" name="Root Zone (50cm)" stroke="#24817a" strokeWidth={2.5} fill="url(#colorSM50)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>

                <div className="insight-box">
                  <Info size={20} />
                  <div>
                    <b>Why Surface Moisture Fluctuates While Root Moisture Lags</b>
                    <p>
                      Surface soil (5 cm) reacts instantaneously to solar radiation and light drizzle, showing extreme diurnal swings.
                      In contrast, the 50 cm root zone acts as a low-pass filter: water requires between 6 and 18 hours to infiltrate through the soil column.
                      By fusing both depths alongside temperature gradients, the LSTM accurately predicts when infiltration will reach plant roots.
                    </p>
                  </div>
                </div>
              </article>
            </div>
          )}

          {/* PAGE 3: MODEL EVALUATION (LSTM vs. PERSISTENCE IN-DEPTH) */}
          {page === "Model Evaluation" && (
            <div style={{ display: "grid", gap: "18px" }}>
              <article className="panel">
                <div className="panel-head">
                  <div>
                    <div className="panel-title">
                      <span className="panel-icon violet">
                        <FlaskConical size={18} />
                      </span>
                      <h2>Scientific Model Evaluation: PyTorch LSTM vs. Naïve Persistence</h2>
                    </div>
                    <p>Why deep learning succeeds where classical persistence baselines fail in time-series hydrology</p>
                  </div>
                </div>

                {/* Tabs */}
                <div style={{ display: "flex", gap: "10px", marginTop: "16px", borderBottom: "1px solid #edf1f7", paddingBottom: "8px" }}>
                  <button
                    className={`outline-btn ${evalTab === "comparison" ? "primary-btn" : ""}`}
                    onClick={() => setEvalTab("comparison")}
                  >
                    Direct Model Comparison
                  </button>
                  <button
                    className={`outline-btn ${evalTab === "theory" ? "primary-btn" : ""}`}
                    onClick={() => setEvalTab("theory")}
                  >
                    Theoretical Justification
                  </button>
                  <button
                    className={`outline-btn ${evalTab === "metrics" ? "primary-btn" : ""}`}
                    onClick={() => setEvalTab("metrics")}
                  >
                    Empirical Test Benchmarks
                  </button>
                </div>

                {/* TAB 1: Direct Model Comparison */}
                {evalTab === "comparison" && (
                  <div className="compare-matrix">
                    <div className="compare-row header">
                      <span>Feature / Dimension</span>
                      <span>Multivariate PyTorch LSTM</span>
                      <span>Naïve Persistence Baseline</span>
                    </div>
                    <div className="compare-row">
                      <span><b>Prediction Formula</b></span>
                      <span>{"ŷ(t+96) = f_θ(X[t-95...t]) via recurrent memory"}</span>
                      <span>{"ŷ(t+96) = y(t) (assumes static moisture)"}</span>
                    </div>
                    <div className="compare-row">
                      <span><b>Infiltration Front Awareness</b></span>
                      <span><b>High:</b> Correlates surface rain spikes with delayed root arrival</span>
                      <span><b>Zero:</b> Completely blind to infiltration until it hits 50 cm</span>
                    </div>
                    <div className="compare-row">
                      <span><b>Evapotranspiration Decay</b></span>
                      <span><b>Learned:</b> Models non-linear desaturation under high ambient heat</span>
                      <span><b>Lagged:</b> Constantly overestimates moisture during dry heatwaves</span>
                    </div>
                    <div className="compare-row">
                      <span><b>Multi-Sensor Fusion</b></span>
                      <span>5 inputs (SM_50cm, SM_5cm, Temp_50cm, Temp_5cm, Rain)</span>
                      <span>1 input (SM_50cm only)</span>
                    </div>
                    <div className="compare-row">
                      <span><b>Actionable Decision Window</b></span>
                      <span><b>24 Hours in Advance</b> (proactive scheduling)</span>
                      <span>0 Hours (reactive alert only after drying happens)</span>
                    </div>
                    <div className="compare-row">
                      <span><b>Test RMSE Error</b></span>
                      <span><b>1.2798 % VWC</b> (reduced peak errors)</span>
                      <span>1.4206 % VWC (~10% higher error variance)</span>
                    </div>
                  </div>
                )}

                {/* TAB 2: Theoretical Justification */}
                {evalTab === "theory" && (
                  <div style={{ display: "grid", gap: "14px", marginTop: "14px" }}>
                    <div className="insight-box">
                      <Layers size={22} />
                      <div>
                        <b>1. The Hydrological Infiltration Lag Paradox</b>
                        <p>
                          In semi-arid soils, precipitation takes between 6 to 18 hours to percolate 50 cm down to the root zone.
                          A Naïve Persistence model simply says: <em>&quot;Soil moisture 24h from now will be whatever it is right now.&quot;</em>
                          When a thunderstorm hits, Persistence reports that the root zone is dry and erroneously calls for irrigation!
                          The LSTM recurrent cell state (C_t) acts as a physical water accumulator, integrating surface rainfall over the 96 time-step window and forecasting the arrival of the infiltration wavefront.
                        </p>
                      </div>
                    </div>

                    <div className="insight-box">
                      <Thermometer size={22} />
                      <div>
                        <b>2. Non-Linear Solar Evapotranspiration Dynamics</b>
                        <p>
                          During hot summer dry periods, topsoil temperature (Temp_5cm) regularly exceeds 35°C, causing rapid soil desaturation.
                          Persistence cannot anticipate continuous moisture loss and perpetually lags behind reality.
                          The LSTM learns the physical coupling between temperature gradients (Temp_5cm - Temp_50cm) and moisture depletion rates, warning farmers 24 hours before moisture reaches the permanent wilting point (10% VWC).
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* TAB 3: Empirical Test Benchmarks */}
                {evalTab === "metrics" && (
                  <div style={{ marginTop: "14px" }}>
                    <div className="metrics three">
                      <div className="metric">
                        <div className="metric-top">
                          <span className="metric-icon mint">
                            <Gauge size={19} />
                          </span>
                          <small>MAE</small>
                        </div>
                        <p>Mean Absolute Error</p>
                        <strong>0.7271<i> % VWC</i></strong>
                      </div>
                      <div className="metric">
                        <div className="metric-top">
                          <span className="metric-icon blue">
                            <Activity size={19} />
                          </span>
                          <small>RMSE</small>
                        </div>
                        <p>Root Mean Squared Error</p>
                        <strong>1.2798<i> % VWC</i></strong>
                      </div>
                      <div className="metric">
                        <div className="metric-top">
                          <span className="metric-icon violet">
                            <ChartNoAxesCombined size={19} />
                          </span>
                          <small>R² Score</small>
                        </div>
                        <p>Variance Explained</p>
                        <strong>0.8623<i> score</i></strong>
                      </div>
                    </div>

                    <p style={{ marginTop: "14px", color: "#7a8ba4", fontSize: "11px", lineHeight: "1.7" }}>
                      * Benchmarks empirically evaluated on <b>52,014 held-out test samples</b> (chronological split: Jan 1, 2024 – Jun 30, 2025).
                      All models evaluated on identical timestamps without lookahead data leakage.
                    </p>
                  </div>
                )}
              </article>
            </div>
          )}

          {/* PAGE 4: IRRIGATION GUIDANCE */}
          {page === "Irrigation Guidance" && (
            <div style={{ display: "grid", gap: "16px" }}>
              <article className="panel">
                <div className="panel-title">
                  <span className="panel-icon mint">
                    <Sprout size={18} />
                  </span>
                  <h2>Agronomic Soil Water Management Thresholds</h2>
                </div>
                <p className="sub">Standard root-zone volumetric water content (VWC) decision bounds for 50 cm depth</p>

                <div className="compare-matrix" style={{ marginTop: "14px" }}>
                  <div className="compare-row header">
                    <span>Moisture Zone</span>
                    <span>Range (% VWC)</span>
                    <span>Agronomic Meaning & Recommended Action</span>
                  </div>
                  <div className="compare-row">
                    <span><b>Field Capacity (Saturation)</b></span>
                    <span>&gt; 35.0%</span>
                    <span>Soil pore space is completely full. Gravitational drainage occurs; no irrigation needed.</span>
                  </div>
                  <div className="compare-row">
                    <span><b>Optimal Root Zone</b></span>
                    <span>18.0% – 35.0%</span>
                    <span>Ideal water availability for transpiration and nutrient uptake. Standard crop growth.</span>
                  </div>
                  <div className="compare-row">
                    <span><b>Management Allowed Depletion (MAD)</b></span>
                    <span>10.0% – 18.0%</span>
                    <span>Deficit alert zone. Irrigation should be scheduled within 24 hours to prevent stress.</span>
                  </div>
                  <div className="compare-row">
                    <span><b>Permanent Wilting Point (PWP)</b></span>
                    <span>&lt; 10.0%</span>
                    <span>Crop roots can no longer extract water against soil matrix suction. Severe yield reduction.</span>
                  </div>
                </div>

                <div className="insight-box" style={{ marginTop: "16px" }}>
                  <HelpCircle size={20} />
                  <div>
                    <b>Smart Irrigation Principle</b>
                    <p>
                      Rather than irrigating immediately when surface soil looks dry, farmers should manage the 50 cm root zone.
                      By using the 24-hour advance forecast, farmers can avoid running expensive pumps when a rain infiltration event is already on its way downward into the soil profile.
                    </p>
                  </div>
                </div>
              </article>
            </div>
          )}

          {/* PAGE 5: SCENARIO DATA EXPLORER */}
          {page === "Scenario Data" && (
            <article className="panel">
              <div className="panel-head">
                <div>
                  <div className="panel-title">
                    <span className="panel-icon blue">
                      <Database size={18} />
                    </span>
                    <h2>Scenario Sensor Sequence (96 Time-Steps, 15m Cadence)</h2>
                  </div>
                  <p>
                    Inspect, paginate, filter, and export the sliding input window fed to the PyTorch LSTM model (
                    {inputMode === "historical" ? `Historical: ${selectedHistoricalId}` : `Simulation: ${selectedScenario}`})
                  </p>
                </div>
                <button className="primary-btn" onClick={exportCsv}>
                  <Download size={14} /> Export CSV ({allTableRows.length} rows)
                </button>
              </div>

              <div style={{ display: "flex", gap: "10px", margin: "14px 0", alignItems: "center", flexWrap: "wrap" }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "8px 12px",
                    border: "1px solid #dce3ed",
                    borderRadius: "8px",
                    background: "#fff",
                    flex: 1,
                    maxWidth: "280px",
                  }}
                >
                  <Search size={14} color="#8a98ad" />
                  <input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search time or date..."
                    style={{ border: 0, outline: 0, fontSize: "11px", width: "100%" }}
                  />
                </div>
                <button className="outline-btn" onClick={() => setSortAsc(!sortAsc)}>
                  Sort {sortAsc ? "Oldest First ↑" : "Newest First ↓"}
                </button>
                <small style={{ color: "#8a98ad", marginLeft: "auto" }}>
                  Total Observations: <b>{allTableRows.length}</b> (24 hours at 15m interval)
                </small>
              </div>

              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "11px", textAlign: "left" }}>
                  <thead>
                    <tr style={{ background: "#f7f9fc", borderBottom: "1px solid #edf1f7", color: "#77879e" }}>
                      <th style={{ padding: "10px 12px" }}>Step</th>
                      <th style={{ padding: "10px 12px" }}>Time (15m Cadence)</th>
                      <th style={{ padding: "10px 12px" }}>SM_50cm (% VWC)</th>
                      <th style={{ padding: "10px 12px" }}>SM_5cm (% VWC)</th>
                      <th style={{ padding: "10px 12px" }}>Temp_50cm (°C)</th>
                      <th style={{ padding: "10px 12px" }}>Temp_5cm (°C)</th>
                      <th style={{ padding: "10px 12px" }}>Rainfall (mm)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginatedRows.map((r) => (
                      <tr key={r.step} style={{ borderBottom: "1px solid #edf1f7" }}>
                        <td style={{ padding: "9px 12px", color: "#8897ad" }}>#{r.step}</td>
                        <td style={{ padding: "9px 12px", fontWeight: 700, color: "#25344f" }}>{r.time}</td>
                        <td style={{ padding: "9px 12px", color: "#1e685c", fontWeight: 600 }}>{r.sm50.toFixed(2)}%</td>
                        <td style={{ padding: "9px 12px" }}>{r.sm5.toFixed(2)}%</td>
                        <td style={{ padding: "9px 12px" }}>{r.temp50.toFixed(1)}°C</td>
                        <td style={{ padding: "9px 12px" }}>{r.temp5.toFixed(1)}°C</td>
                        <td style={{ padding: "9px 12px", color: r.rain > 0 ? "#2b70b5" : "#8897ad" }}>
                          {r.rain > 0 ? `${r.rain.toFixed(1)} mm` : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination Controls */}
              <div className="pagination-bar">
                <span>
                  Showing {allTableRows.length > 0 ? (tablePage - 1) * PAGE_SIZE + 1 : 0} –{" "}
                  {Math.min(tablePage * PAGE_SIZE, allTableRows.length)} of {allTableRows.length} observations
                </span>
                <div className="pagination-controls">
                  <button
                    className="outline-btn"
                    disabled={tablePage === 1}
                    onClick={() => setTablePage((p) => Math.max(1, p - 1))}
                    style={{ padding: "4px 8px", fontSize: "11px" }}
                  >
                    <ChevronLeft size={13} style={{ display: "inline", verticalAlign: "middle" }} /> Prev
                  </button>
                  <span style={{ fontWeight: 700, margin: "0 4px" }}>
                    Page {tablePage} of {totalPages}
                  </span>
                  <button
                    className="outline-btn"
                    disabled={tablePage >= totalPages}
                    onClick={() => setTablePage((p) => Math.min(totalPages, p + 1))}
                    style={{ padding: "4px 8px", fontSize: "11px" }}
                  >
                    Next <ChevronRight size={13} style={{ display: "inline", verticalAlign: "middle" }} />
                  </button>
                </div>
              </div>
            </article>
          )}

          {/* Footer */}
          <footer>
            <span>
              <i>
                <Droplets size={13} />
              </i>
              SOILCAST <b>/</b> SMART IRRIGATION INFERENCE ENGINE
            </span>
            <span>
              <i style={{ width: "6px", height: "6px", borderRadius: "50%", background: "#38b58a", display: "inline-block" }} />
              PYTORCH LSTM INFERENCE READY · 24-HOUR ADVANCE FORECAST
            </span>
          </footer>
        </div>
      </section>
    </main>
  );
}
