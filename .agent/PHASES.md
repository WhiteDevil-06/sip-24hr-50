# Phased Project Roadmap & Phase Gate Specifications

This document defines the 10 sequential phases of the project. Every phase has a designated owner, prerequisites, strict acceptance criteria, required validation checks, and human sign-off gates.

---

## Phase 0: Project and Agent-System Initialization
- **Owner:** Project Lead (assisted by Coding Assistant)
- **Dependencies:** None
- **Acceptance Criteria:**
  - Workspace and Git repository initialized cleanly.
  - Core directory structure established (`.agent/`, `docs/`, `data/`, `frontend/`, `backend/`, `tests/`).
  - Shared instructions, `.agent/GLOBAL_RULES.md`, `.agent/PHASES.md`, `.agent/PROJECT_STATE.md`, `.agent/AGENT_REGISTRY.md` created.
  - Role definition files created with strict ownership boundaries.
  - Role selection mechanism implemented (`ACTIVE_ROLE` + `.agent/ACTIVE_ROLE.local`).
  - `.gitignore` configured to prevent committing secrets, large datasets, and virtual environments.
  - Tool and environment realities verified (Python 3.13.3, Git, Node/npm verified; absence of native autonomous subagent tools documented).
  - No model training, preprocessing, backend code, or frontend code implemented prematurely.
- **Validation:**
  - Instruction discovery verification.
  - Git status verification.
  - Tool paths and environment checks.
- **Phase Gate:** Explicit human approval by Project Lead required to proceed to Phase 1.

---

## Phase 1: Dataset Audit
- **Owner:** Project Lead
- **Dependencies:** Phase 0 approved complete; IISc Berambadi raw dataset downloaded into `data/raw/`.
- **Acceptance Criteria:**
  - Verify file existence, format, headers, and column names.
  - Audit timestamps: verify sampling interval (e.g., 15 minutes = 96 steps/24h), identify gaps, duplicates, and irregular intervals.
  - Audit `SM_50cm` target variable: check distributions, missing values, physically impossible values, and sensor drift.
  - Audit environmental features: rainfall, temperature, relative humidity, solar radiation, etc.
  - Compute actual descriptive statistics and log them in `docs/EXPERIMENTS.md`.
  - Formulate and justify a strict chronological train/val/test split plan (e.g., 70% train, 15% val, 15% test chronologically).
- **Validation:**
  - Data quality audit script execution.
  - Statistical summary verification.
- **Phase Gate:** Explicit human approval of chronological split boundary before preprocessing starts.

---

## Phase 2: Preprocessing Pipeline
- **Owner:** Project Lead
- **Dependencies:** Phase 1 approved complete.
- **Acceptance Criteria:**
  - Implement reproducible, deterministic time-series preprocessing.
  - Chronological splits applied before fitting any scalers or imputers (zero data leakage).
  - Scalers/imputers fit solely on training data and serialized into artifacts for downstream inference.
  - Sequence generator constructed: input window (e.g., past $T$ steps) mapping to target window 24h into the future (`SM_50cm` at $t + 96$).
  - Automated unit tests validating tensor shapes, sequence alignment, and absence of target leakage.
- **Validation:**
  - Pytest unit tests for sequence shapes and timestamp alignment.
  - Scaler serialization check.
- **Phase Gate:** Project Lead verification of sequence alignment and scaler isolation.

---

## Phase 3: Persistence Baseline
- **Owner:** Project Lead
- **Dependencies:** Phase 2 approved complete.
- **Acceptance Criteria:**
  - Implement Naïve Persistence forecasting baseline: $\hat{y}_{t+96} = y_t$.
  - Evaluate persistence predictions across validation and test sets.
  - Calculate actual baseline metrics: MAE, RMSE, and R².
  - Record baseline metrics in `docs/EXPERIMENTS.md` as the official benchmark.
  - Document educational explanation of why persistence is an essential reference point for time series.
- **Validation:**
  - Baseline evaluation script run on test split.
  - Verification of mathematical correctness of metric functions.
- **Phase Gate:** Project Lead sign-off on baseline performance metrics.

---

## Phase 4: LSTM Learning & Implementation
- **Owner:** Project Lead (Interactive Learning Phase)
- **Dependencies:** Phase 3 approved complete.
- **Acceptance Criteria:**
  - Educational explanation of LSTM architecture: cell state, forget gate, input gate, output gate, hidden units, time steps, features, loss function (MSE), optimizer (Adam).
  - Small, modular implementation of minimal univariate LSTM (historical `SM_50cm` $\to$ future `SM_50cm`).
  - Model training with early stopping, learning curve inspection, and loss logging.
  - Prevention and diagnosis of overfitting.
  - Serialization of trained model artifact (e.g., Keras `.keras` format) along with feature metadata and scaling factors.
  - Verification that saved model artifact can be reloaded and perform inference independently without retraining.
- **Validation:**
  - Training loss convergence verification.
  - Standalone inference check from saved artifact.
- **Phase Gate:** Project Lead confirms complete conceptual understanding and approves trained artifact.

---

## Phase 5: Experiments & Model Evaluation
- **Owner:** Project Lead
- **Dependencies:** Phase 4 approved complete.
- **Acceptance Criteria:**
  - Formulate approved alternative input configurations (e.g., univariate vs. multivariate with atmospheric variables vs. reduced configurations).
  - Train approved configurations under identical chronological splits and hyperparameter disciplines.
  - Fair evaluation against Persistence baseline on held-out test set using MAE, RMSE, and R².
  - Literature check: confirm claims are supported by experimental evidence before claiming novelty.
  - Select winning model artifact for production serving.
  - Create formal Model Handoff Contract (`docs/API_CONTRACT.md` and handoff bundle) for Rahul.
- **Validation:**
  - Benchmark evaluation suite run against test set.
  - Verification of model handoff checklist.
- **Phase Gate:** Project Lead formal approval of handoff bundle to Rahul.

---

## Phase 6: Backend & Model Serving
- **Owner:** Rahul
- **Dependencies:** Phase 5 approved complete; formal Model Handoff Contract received from Project Lead.
- **Acceptance Criteria:**
  - Implement FastAPI serving application in `backend/`.
  - Load saved model and preprocessing artifacts once at application startup (never during prediction request).
  - Implement `/health` and `/predict` endpoints.
  - Validate incoming payloads strictly using Pydantic (data types, array lengths, feature ordering, timestamp monotonicity).
  - Apply exact approved preprocessing transformation to input sequence.
  - Run inference using loaded model; return typed 24-hour forecast response.
  - Verify inference numerical parity: backend `/predict` output must match direct model inference within float precision ($< 10^{-5}$).
  - Full error handling (400 for malformed input, 503 for uninitialized model, finite value checks).
  - Automated API and unit tests.
- **Validation:**
  - Pytest API test suite.
  - Numerical parity test between direct inference and FastAPI endpoint.
- **Phase Gate:** Rahul presents parity verification report; Project Lead approves.

---

## Phase 7: Website Development
- **Owner:** Ram Charan
- **Dependencies:** Phase 5 (Mock Contract available) or Phase 6 (Live API).
- **Acceptance Criteria:**
  - Build Next.js web application (TypeScript, App Router, Tailwind CSS) in `frontend/`.
  - Modern, responsive dashboard layout with accessible components.
  - Interactive charts using Recharts:
    - Historical soil moisture timeline.
    - 24-hour future forecast curve (`SM_50cm` at 15-minute intervals).
    - Threshold-based irrigation recommendation card (e.g., water deficit alert vs. optimal moisture).
  - Model metrics comparison panel (displaying real verified metrics from Phase 5).
  - Explicit UI states: loading spinner/skeleton, empty data state, client validation error, backend connection error.
  - Strict TypeScript types, lint clean, successful production build (`npm run build`).
- **Validation:**
  - Type check (`tsc --noEmit`), ESLint check, and Next.js build validation.
  - Procedural UI and accessibility review.
- **Phase Gate:** Ram Charan presents build validation; Project Lead reviews.

---

## Phase 8: Integration
- **Owner:** Project Lead (supported by Ram Charan and Rahul)
- **Dependencies:** Phase 6 and Phase 7 approved complete.
- **Acceptance Criteria:**
  - Connect Next.js frontend to FastAPI backend via configured environment variables.
  - Validate end-to-end request/response cycle with live server.
  - Verify CORS, timestamp formatting, units, and latency.
  - Verify that forecast displayed on web dashboard matches backend prediction exactly.
  - Verify graceful degradation when backend service is paused or returns errors.
- **Validation:**
  - End-to-end integration test execution.
  - Visual verification in browser.
- **Phase Gate:** Project Lead signs off on integrated application.

---

## Phase 9: Final Validation & Demonstration
- **Owner:** Project Lead (with full team)
- **Dependencies:** Phase 8 approved complete.
- **Acceptance Criteria:**
  - Run all automated test suites (ML, backend, frontend, E2E).
  - Audit security: no exposed keys, proper input validation, safe dependencies.
  - Audit scientific documentation: `docs/EXPERIMENTS.md`, `docs/DECISIONS.md`, `README.md` completely up to date.
  - Re-verify reproducibility: model artifact generates identical metrics when evaluated on clean test split.
  - Prepare demonstration walkthrough and presentation materials.
  - Document real academic limitations, edge cases, and future research directions.
- **Validation:**
  - Full test suite execution across repositories.
  - Security and dependency audit.
- **Phase Gate:** Final project sign-off and demonstration approval by Project Lead.
