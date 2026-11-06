# Verified Project Facts & Technical Reference
## Deep Learning-Based Soil Moisture Prediction for Smart Irrigation

This document is the authoritative, evidence-backed reference sheet of all empirically verified facts, parameters, evaluation benchmarks, and artifact specifications across the repository.

---

## 1. Problem Formulation & Scope

- **Project Title:** Deep Learning-Based Soil Moisture Prediction for Smart Irrigation
- **Primary Research Objective:** 24-hour advance forecasting of root-zone soil moisture at 50 cm depth (`SM_50cm`)
- **Forecasting Cadence ($\Delta t$):** Exactly 15 minutes (99.824% of consecutive transitions in dataset)
- **Forecast Horizon ($H$):** 24 hours ahead = **96 time steps** ($24 \text{ hours} \times 4 \text{ steps/hour}$)
- **Input Sequence Length ($T$):** Past 24 hours = **96 historical time steps**
- **Target Variable:** `SM_50cm` (% Volumetric Water Content, VWC)
- **Scope Boundary:** Academic research, simulation engine, and API serving. Hardware actuator microcontrollers (e.g. ESP32, relay switches) are explicitly excluded from scope.

---

## 2. Dataset & Sampling Facts

- **Dataset Source:** IISc Berambadi / Bechanahalli Watershed, Chamarajanagar District, Karnataka, Southern India
- **Zenodo Archive Record:** [Zenodo 22109968](https://zenodo.org/records/22109968)
- **Total Audited Annual Files:** 10 annual CSV releases (2016 through 2025 in `data/raw/`)
- **Total Raw Records:** 286,062 timestamps
- **Timestamp Regularity:**
  - Exactly 15-minute intervals: **285,549 transitions (99.824%)**
  - Logging boundary gaps ($> 15$ min): **503 transitions (0.176%)**
- **Sensor Shift & Excluded Year:**
  - 2016–2020: Electrical Conductivity (EC) probes
  - 2021: Hardware re-instrumentation transition year (**67.1% missing data at 50 cm depth**; excluded from training)
  - 2022–2025: Modern Relative Dielectric Permittivity (RDP) sensors (**0.0000% missing data** on core features across 119,940 consecutive rows)
- **Soil Hydrologic Inertia:** Autocorrelation of `SM_50cm` at lag 96 (24 hours) is **$r = 0.9141$**

---

## 3. Features & Data Splits

### 3.1 Input Feature Schema
All models consume subsets or the entirety of the 5 standardized features:
1. `SM_50cm`: Deep root-zone soil moisture (% VWC) — Autoregressive input
2. `SM_5cm`: Surface layer soil moisture (% VWC) — Early indicator of infiltration
3. `Temp_50cm`: Deep root-zone soil temperature (°C) — Thermal buffer
4. `Temp_5cm`: Surface layer soil temperature (°C) — Evapotranspiration driver
5. `Precipitation`: Cumulative rainfall depth per 15-minute slot (mm/15min)

### 3.2 Chronological Partitioning (Zero Data Leakage)
- **Training Split:** January 1, 2016 – December 31, 2022 (excluding 2021 transition year)
  - Rows: **166,742 raw rows** $\rightarrow$ **124,196 valid sliding windows**
- **Validation Split:** January 1, 2023 – December 31, 2023
  - Rows: **34,480 raw rows** $\rightarrow$ **33,716 valid sliding windows**
- **Held-Out Test Split:** January 1, 2024 – June 30, 2025
  - Rows: **52,396 raw rows** $\rightarrow$ **52,014 valid sliding windows**
- **MinMax Normalization:** Scalers (`MinMaxScaler(feature_range=(0, 1))`) fitted **strictly on the Training Split** ($N=166,742$). Validation and Test splits are transformed using training scale factors without re-fitting.

---

## 4. Model Architectures & Training Configurations

### 4.1 PyTorch SoilMoistureLSTM Architecture
- **Model Class:** `SoilMoistureLSTM` in [`src/model.py`](file:///c:/Users/raksh/ANN/src/model.py)
- **Recurrent Core:** 2-layer LSTM (`hidden_size=64`, `batch_first=True`, `dropout=0.2`)
- **Regression Head:** `Linear(64, 32)` $\rightarrow$ `ReLU()` $\rightarrow$ `Dropout(0.2)` $\rightarrow$ `Linear(32, 1)`
- **Output:** Scalar prediction `[batch_size]` representing forecasted `SM_50cm` at $t + 96$
- **Total Trainable Parameters:**
  - Multivariate Model (5 features): **52,865 parameters**
  - Univariate Model (1 feature): **51,841 parameters**

### 4.2 Training Hyperparameters
- **Loss Function:** Mean Squared Error (MSE)
- **Optimizer:** Adam (`lr=0.001`)
- **Gradient Clipping:** `max_norm=1.0` (prevents recurrent gradient explosion)
- **Learning Rate Scheduler:** `ReduceLROnPlateau(mode='min', factor=0.5, patience=2)`
- **Batch Size:** 512
- **Early Stopping:** Patience = 3 epochs monitoring validation loss
- **Checkpointing:** State dictionary saved to `models/best_model.pt` on validation loss improvement

---

## 5. Verified Empirical Evaluation Benchmarks

Evaluated on the **52,014 held-out test samples** (Jan 1, 2024 – Jun 30, 2025) in physical units (% VWC):

### 5.1 Aggregate Test Metrics
| Model | Input Configuration | Test MAE (% VWC) | Test RMSE (% VWC) | Test $R^2$ Score | Status |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Naïve Persistence** | `SM_50cm(t)` | 0.6949 | 1.4206 | 0.8303 | Reference Baseline |
| **Univariate LSTM** | `SM_50cm(t-95...t)` | 0.6639 | 1.2772 | 0.8628 | Candidate |
| **Multivariate LSTM** | **5 Features** | **0.7271** | **1.2798** | **0.8623** | **Champion (Deployed)** |

### 5.2 Slice Analysis: Rain Events ($N=13,712$ samples where 24h Rain $> 1$ mm)
| Model | MAE (% VWC) | RMSE (% VWC) | $R^2$ Score | Advantage |
| :--- | :---: | :---: | :---: | :--- |
| **Persistence** | 0.8150 | 1.6360 | 0.6255 | Baseline |
| **Univariate LSTM** | 0.7854 | 1.4590 | 0.7022 | +10.8% RMSE improvement |
| **Multivariate LSTM** | **0.7640** | **1.4008** | **0.7255** | **+14.4% RMSE improvement (Best)** |

### 5.3 Slice Analysis: High Transitions ($N=8,261$ samples where $|y_{t+96} - y_t| > 1.0\%$ VWC)
| Model | MAE (% VWC) | RMSE (% VWC) | $R^2$ Score | Advantage |
| :--- | :---: | :---: | :---: | :--- |
| **Persistence** | 2.5754 | 3.4296 | 0.2296 | Baseline (Collapses) |
| **Univariate LSTM** | 2.0293 | 2.9690 | 0.4226 | +13.4% RMSE improvement |
| **Multivariate LSTM** | **1.9811** | **2.9063** | **0.4467** | **+15.2% RMSE improvement (Best)** |

### 5.4 Error Distribution (Tail Percentiles)
| Model | Median Absolute Error | 90th Percentile | 95th Percentile | 99th Percentile | Max Error |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Persistence** | 0.4000 % | 1.5000 % | 2.6000 % | 5.8870 % | 32.3000 % |
| **Univariate LSTM** | 0.3903 % | 1.3035 % | 2.1891 % | 5.3933 % | 32.1687 % |
| **Multivariate LSTM** | 0.5119 % | **1.2676 %** | **2.0846 %** | **5.3481 %** | **31.9320 %** |

---

## 6. Model Artifacts & File Locations

| Artifact File | Path | Size | Description |
| :--- | :--- | :---: | :--- |
| **Multivariate Weights** | `models/best_model.pt` | 219,061 bytes | PyTorch checkpoint state dict for 5-feature champion |
| **Univariate Weights** | `models/lstm_univariate.pt` | 215,055 bytes | PyTorch checkpoint state dict for 1-feature fallback |
| **Feature Scaler** | `models/feature_scaler.pkl` | 829 bytes | Pickled scikit-learn `MinMaxScaler` (5 features) |
| **Target Scaler** | `models/target_scaler.pkl` | 620 bytes | Pickled scikit-learn `MinMaxScaler` (`SM_50cm`) |
| **Scaler Metadata** | `models/scaler_metadata.json` | 733 bytes | Pure JSON scale factors and offsets for non-sklearn inference |
| **Model Metadata** | `models/model_metadata.json` | 908 bytes | Architecture spec, metric benchmarks, and irrigation thresholds |

---

## 7. Backend Serving & Numerical Parity Guarantee

- **Backend Framework:** FastAPI 0.162.0 + Uvicorn 0.54.0 + Pydantic 2.14.2
- **Launcher:** [`backend/run.py`](file:///c:/Users/raksh/ANN/backend/run.py) (default host `127.0.0.1`, port `8000`)
- **Key Endpoints:**
  - `GET /`: Navigation directory and service overview
  - `GET /health` & `GET /api/health`: Health status, model loaded confirmation, timestamp
  - `POST /api/v1/predict`: 96-step sequence validation, MinMax scaling, PyTorch CPU inference, unscaling, and advisory generation
  - `GET /api/forecast`: Frontend-ready scenario payload
  - `GET /api/v1/metrics`: Verified empirical evaluation table across all three models
- **Numerical Parity Guarantee:**
  $$| \hat{y}_{\text{FastAPI}} - \hat{y}_{\text{PyTorch Direct}} | < 10^{-5}$$
  Verified by regression test `tests/test_backend_api.py::TestNumericalParity::test_parity`.

---

## 8. Frontend Dashboard & Simulator

- **Frontend Framework:** Next.js 15.5.28 (App Router), React 19, TypeScript, Tailwind CSS 3.4.17, Recharts 2.15.0, Lucide React
- **Entry Point:** [`frontend/app/page.tsx`](file:///c:/Users/raksh/ANN/frontend/app/page.tsx)
- **Features:**
  - Collapsible desktop sidebar (252px drawer $\longleftrightarrow$ 68px icon-only rail)
  - Custom slim teal-accented scrollbars (`globals.css`)
  - SoilCast brand droplet favicon (`app/icon.svg`)
  - Next.js dev overlay indicator suppressed (`next.config.ts: devIndicators: false`)
  - 4 Agricultural simulation scenarios (Summer Drought, Monsoon Infiltration, Drying Cycle, Custom Sliders)
  - Interactive trajectory chart plotting Past Observed (50 cm), LSTM 24h Forecast, and Naïve Persistence Flatline
  - In-depth comparative Model Evaluation with tabs for Direct Comparison, Infiltration Lag Theory, and Empirical Benchmarks
  - 96-step chronological data inspection table with CSV export

---

## 9. Agronomic Logic & Soil Physical Thresholds

Configured in [`backend/app/inference.py`](file:///c:/Users/raksh/ANN/backend/app/inference.py) and [`models/model_metadata.json`](file:///c:/Users/raksh/ANN/models/model_metadata.json):
- **Permanent Wilting Point (PWP):** $10.0\%$ VWC ($\hat{y} < 10.0\% \rightarrow$ `CRITICAL_DEFICIT`, immediate urgency)
- **Management Allowed Depletion (MAD):** $14.0\% - 18.0\%$ VWC ($\hat{y} < 18.0\% \rightarrow$ `DEFICIT_ALERT`, high urgency)
- **Optimal Root-Zone Range:** $18.0\% - 28.0\%$ VWC (`OPTIMAL_MOISTURE`, no action required)
- **Field Capacity (Saturation):** $35.0\%$ VWC ($\hat{y} > 35.0\% \rightarrow$ `EXCESS_MOISTURE`, drainage check)
- **Domain Note:** Calibrated for Sandy Clay Loam / Red Ferralsols of the Berambadi watershed in southern Karnataka; requires re-calibration for coarse sands or vertisols.

---

## 10. Automated Test Suite Results

- **Command:** `.\.venv\Scripts\python.exe -m pytest tests/ -v`
- **Total Tests Collected:** 34
- **Passed:** **34 (100% pass rate)**
- **Failed:** 0
- **Skipped:** 0
- **Test Categories:**
  - `test_preprocessing.py`: 4 tests (Chronological split, zero lookahead leakage, scaler isolation, 96-step window alignment)
  - `test_baseline.py`: 2 tests (Lag-96 persistence logic, unscaled metric calculation)
  - `test_model.py`: 2 tests (Univariate & multivariate PyTorch forward pass tensors)
  - `test_metrics.py`: 3 tests (MAE, RMSE, R² mathematical exactness)
  - `test_backend_api.py`: 10 tests (Health, metrics, prediction validation, error handling, numerical parity $< 10^{-5}$)
  - `test_integration.py`: 6 tests (CORS preflight, forecast contract shape, error handling)
  - `test_final_validation.py`: 7 tests (Zero hardcoded secrets, .env.local gitignore, documentation presence, physical prediction range [0, 60]%)

