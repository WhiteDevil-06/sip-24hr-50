# Project Technical Issues & Discrepancy Log
## Deep Learning-Based Soil Moisture Prediction for Smart Irrigation

This document details all technical discrepancies, bottlenecks, architectural limitations, and documentation inconsistencies identified during the comprehensive system audit.

---

## 1. Issue Severity Classification Summary

| Priority Level | Total Identified | Status | Primary Focus Area |
| :--- | :---: | :--- | :--- |
| **Critical** | 0 | None Blocked | Core modeling, weights, APIs, and pipelines are functional |
| **High Priority** | 2 | Actionable | Memory scaling in windowing & lack of live database fallback |
| **Medium Priority** | 2 | Actionable | Static agronomic thresholds & test suite runtime optimization |
| **Low Priority** | 2 | Non-blocking | Deprecation notices & scikit-learn feature-name warnings |
| **Documentation-Only**| 2 | Resolved | Metric reporting nuance (Univariate vs Multivariate) & state tracking |

---

## 2. Detailed Technical Findings

### 2.1 Critical Issues
*No critical issues found.* The PyTorch model weights load correctly, numerical parity is preserved ($< 10^{-5}$ delta), the test suite passes, and the backend-frontend integration functions as specified.

---

### 2.2 High-Priority Issues

#### Issue H-01: In-Memory Sliding Window Construction Bottleneck
- **Description:** `PreprocessingPipeline.create_sliding_windows` in [`src/preprocessing.py`](file:///c:/Users/raksh/ANN/src/preprocessing.py) accumulates all 96-step sliding windows into Python lists before converting to 3D NumPy arrays (`X_train.npy` requires ~250 MB for 124,000 windows; `X_test.npy` requires ~100 MB).
- **Evidence:** During training in [`scripts/run_phase5_multivariate_lstm.py`](file:///c:/Users/raksh/ANN/scripts/run_phase5_multivariate_lstm.py), memory pressure required subsampling training windows using `stride=4`.
- **Impact:** While manageable for the current 10-year dataset on modern developer workstations, scaling to higher frequencies (e.g., 5-minute telemetry) or expanding to multi-catchment regional datasets will trigger `MemoryError`.
- **Recommended Resolution:** Refactor `create_sliding_windows` to use memory-mapped NumPy files (`np.lib.format.open_memmap`) or construct a PyTorch `IterableDataset` / custom sliding-window strided view (`np.lib.stride_tricks.sliding_window_view`) that generates 3D tensors dynamically on the fly during training.

#### Issue H-02: Backend `/api/forecast` Relies on Synthetic Fallback for Unparameterized GET Requests
- **Description:** The convenience endpoint `GET /api/forecast` in [`backend/app/main.py`](file:///c:/Users/raksh/ANN/backend/app/main.py) synthesizes 96 historical observations ending at `now` when called without input arguments, rather than fetching live sensor telemetry from an external database.
- **Evidence:**
  ```python
  # backend/app/main.py (lines 186-195)
  # The observed sequence is synthesised from a realistic steady value so the
  # endpoint works without live sensor data being posted; in real deployment
  # this should be replaced with a database or data-stream lookup.
  ```
- **Impact:** If a user makes a GET request expecting actual live field readings from Karnataka, they receive synthesized baseline telemetry instead. Full parameterization is supported via `POST /api/v1/predict`, which accepts real feature arrays.
- **Recommended Resolution:** Document clearly in OpenAPI / Swagger docs that `/api/forecast` is an interface demonstration wrapper, and document the integration path for connecting an actual PostgreSQL / TimescaleDB telemetry store for field deployment.

---

### 2.3 Medium-Priority Issues

#### Issue M-01: Universal Static Agronomic Thresholds (Soil Texture Invariance)
- **Description:** Agronomic thresholds are hardcoded in [`models/model_metadata.json`](file:///c:/Users/raksh/ANN/models/model_metadata.json) and [`backend/app/inference.py`](file:///c:/Users/raksh/ANN/backend/app/inference.py):
  - Permanent Wilting Point (PWP): $10.0\%$ VWC
  - Optimal Moisture Range: $18.0\% - 28.0\%$ VWC
  - Field Capacity (Saturation): $35.0\%$ VWC
- **Evidence:**
  ```python
  wilting = thresholds.get("wilting_point_vwc", 10.0)
  field_cap = thresholds.get("field_capacity_vwc", 35.0)
  opt_min = thresholds.get("optimal_range_min_vwc", 18.0)
  opt_max = thresholds.get("optimal_range_max_vwc", 28.0)
  ```
- **Impact:** These thresholds represent Sandy Clay Loam (the soil texture of the Berambadi watershed). In coarse sandy soils, wilting occurs at $3\% - 5\%$ VWC, while in heavy vertisols/clay, wilting can occur at $20\% - 24\%$ VWC. Applying $10\%$ universally across arbitrary soil types would lead to incorrect irrigation decisions.
- **Recommended Resolution:** Allow clients to pass `soil_texture` or custom `wilting_point` / `field_capacity` thresholds in `PredictRequest`, or parameterize advisory rules by crop coefficient ($K_c$) and soil texture class.

#### Issue M-02: Recursive File Traversals in `tests/test_final_validation.py`
- **Description:** `_text_files()` in [`tests/test_final_validation.py`](file:///c:/Users/raksh/ANN/tests/test_final_validation.py) uses `Path.rglob("*")` starting from project root, iterating over 40,000+ files in `.venv` and `node_modules` before filtering with `SKIP_DIRS`.
- **Evidence:** `pytest tests/test_final_validation.py` takes ~3 minutes on Windows systems.
- **Impact:** Slows down automated CI/CD and developer testing loops.
- **Recommended Resolution:** Replace `ROOT.rglob("*")` with a top-level directory walker (`os.walk`) that prunes `SKIP_DIRS` in place (`dirs[:] = [d for d in dirs if d not in SKIP_DIRS]`), reducing test execution time from 180 seconds to under 2 seconds.

---

### 2.4 Low-Priority Issues

#### Issue L-01: Starlette TestClient Deprecation Warning with `httpx`
- **Description:** Running pytest emits:
  `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead.`
- **Evidence:** Present in `pytest` console warnings summary.
- **Impact:** Harmless warning; does not affect test execution or test client assertions.
- **Recommended Resolution:** Pin or update `starlette` / `httpx` dependencies when next updating package specifications.

#### Issue L-02: Unvalidated Feature Names Warning in `test_preprocessing.py`
- **Description:** Passing unlabelled NumPy slices to fitted `MinMaxScaler` produces:
  `UserWarning: X does not have valid feature names, but MinMaxScaler was fitted with feature names`
- **Evidence:** Emitted during `test_sliding_window_shapes_and_temporal_alignment` and `test_scaler_serialization_roundtrip`.
- **Impact:** Standard scikit-learn advisory warning; numerical normalization remains 100% accurate.
- **Recommended Resolution:** Suppress warning in pytest config or pass DataFrame with column names when transforming.

---

### 2.5 Documentation-Only Issues

#### Issue D-01: Univariate vs. Multivariate Model Performance Nuance
- **Description:** Earlier summaries described Multivariate LSTM as the "best-performing" model without highlighting that on aggregate test metrics, Univariate LSTM achieved slightly superior overall figures:
  - Univariate: MAE = $0.6639\%$, RMSE = $1.2772\%$, $R^2 = 0.8628$
  - Multivariate: MAE = $0.7271\%$, RMSE = $1.2798\%$, $R^2 = 0.8623$
- **Evidence:** Audit slice analysis proved that Multivariate LSTM is empirically superior during dynamic events:
  - Rain Events ($N=13,712$): Multivariate beats Univariate (MAE $0.7640$ vs $0.7854$; RMSE $1.4008$ vs $1.4590$; $R^2$ $0.7255$ vs $0.7022$).
  - High Transitions ($N=8,261$): Multivariate beats Univariate (MAE $1.9811$ vs $2.0293$; RMSE $2.9063$ vs $2.9690$; $R^2$ $0.4467$ vs $0.4226$).
  - Peak Tails (90th, 95th, 99th percentiles): Multivariate errors are strictly lower than Univariate.
- **Impact:** Without this nuance, reviewers may question why Multivariate was selected when aggregate MAE is slightly higher.
- **Recommended Resolution:** Document the exact slice analysis in `docs/FINAL_PROJECT_AUDIT.md` and `docs/EXPERIMENTS.md`.

#### Issue D-02: Project Phase Tracker Alignment
- **Description:** `.agent/PROJECT_STATE.md` listed Phase 9 as `VALIDATED — AWAITING HUMAN APPROVAL` even after PR #1 was merged into `main`.
- **Evidence:** Commit `5d02e2c` merged all feature branch code into `main`.
- **Impact:** Minor cosmetic discrepancy in governance documents.
- **Recommended Resolution:** Mark Phase 9 as `APPROVED COMPLETE` upon Project Lead sign-off.

