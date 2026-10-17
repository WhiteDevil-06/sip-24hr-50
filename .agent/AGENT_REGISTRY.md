# Specialist Reviewer Registry & Procedural Protocols

This document defines the 11 specialized reviewer roles responsible for quality, safety, and scientific integrity across all project phases.

> [!IMPORTANT]
> **Tool & Execution Reality Notice:**
> In this Antigravity environment, native autonomous code-review subagents are not registered as standalone executable tools. Therefore, per **Rule K** and **Section 8** of the Master Prompt, all specialist reviews must be executed as **explicit, documented procedural checklists**. An agent must never label its own procedural self-review as an independent subagent execution.

---

## Specialist Catalog

| Specialist | Identifier | Primary Domain | Mandatory Triggers |
| :--- | :--- | :--- | :--- |
| **Orchestrator** | `orchestrator` | Task lifecycle & role boundary enforcement | Every user task initiation and completion |
| **Planner** | `planner` | Minimal diff planning & acceptance criteria | Before making any substantial code modification |
| **Code Reviewer** | `code-reviewer` | Code cleanliness, maintainability, scope check | Every code modification |
| **Test Validator** | `test-validator` | Test suite runs, linting, typing, build checks | Every meaningful implementation change |
| **Security Reviewer** | `security-reviewer` | Secrets, safe configuration, input sanitization | Any file with env variables, API endpoints, or user inputs |
| **Data Quality Reviewer** | `data-quality-reviewer` | Schema, timestamps, sensor anomalies, missingness | Dataset audit, cleaning, and transformation |
| **ML Integrity Reviewer** | `ml-integrity-reviewer` | Temporal leakage, horizon alignment, metrics | Preprocessing, baseline, LSTM training, evaluation |
| **Frontend Reviewer** | `frontend-reviewer` | Next.js, TypeScript, Recharts, UI accessibility | Any modification in `frontend/` |
| **Backend Reviewer** | `backend-reviewer` | FastAPI, Pydantic, inference parity, error handling | Any modification in `backend/` |
| **Integration Reviewer** | `integration-reviewer` | E2E contracts, payload parity, latency, CORS | Changes to API contracts, handoff, or integration |
| **Documentation Reviewer**| `documentation-reviewer` | ADRs, experiment records, sync with code | Any change altering behavior, phase, or contracts |

---

## 1. Orchestrator
- **Purpose:** Coordinates the execution of tasks, enforces active role boundaries, prevents scope leakage across phases, and aggregates review outputs.
- **Trigger:** Beginning and end of every user request or coding session.
- **Required Inputs:** User request, active role (`.agent/ACTIVE_ROLE` or `.agent/ACTIVE_ROLE.local`), `PROJECT_STATE.md`.
- **Validation Tasks:**
  1. Confirm that proposed work belongs strictly to the active phase.
  2. Confirm that proposed work does not violate role ownership boundaries.
  3. Ensure required specialist reviews are triggered upon code modification.
- **Expected Report:** Consolidated summary of reviews, verification results, blockers, and next phase gate status.

---

## 2. Planner
- **Purpose:** Analyzes the task and proposes a minimal, surgical plan before making edits.
- **Trigger:** Prior to implementing any code, configuration, or architectural change.
- **Required Inputs:** Task description, active role, current codebase state.
- **Validation Tasks:**
  1. Define explicit acceptance criteria.
  2. Identify the smallest necessary diff.
  3. Enumerate dependencies, risks, and required specialist reviewers.
- **Expected Report:** Step-by-step plan with file targets, acceptance criteria, and deferred tasks.

---

## 3. Code Reviewer
- **Purpose:** Inspects actual diffs for coding standards, maintainability, scope containment, and regressions.
- **Trigger:** Immediately after code edits are applied.
- **Required Inputs:** Git diff, affected files, language-specific guidelines.
- **Validation Tasks:**
  1. Verify diff touches only files within the planned scope.
  2. Ensure code is readable, modular, and cleanly documented.
  3. Ensure existing docstrings and comments are preserved unless explicitly refactored.
- **Expected Report:** Pass/Fail finding on diff cleanliness, scope containment, and identified code defects.

---

## 4. Test Validator
- **Purpose:** Executes automated tests, type checkers, linters, and build checks.
- **Trigger:** After code edits are made.
- **Required Inputs:** Test files (`tests/`), test runners (Pytest, npm test, tsc).
- **Validation Tasks:**
  1. Execute applicable tests using terminal runner.
  2. Capture exact commands and stdout/stderr.
  3. Verify tests are not modified or assertions weakened to falsely pass.
- **Expected Report:** Table of executed test commands, passed/failed counts, and log snippets.

---

## 5. Security Reviewer
- **Purpose:** Prevents credential leaks, ensures safe configuration, and validates input sanitization.
- **Trigger:** Modifications to configuration files, environment variables, dependencies, or network endpoints.
- **Required Inputs:** Diff of configuration, backend endpoints, and frontend client calls.
- **Validation Tasks:**
  1. Check for hardcoded API keys, tokens, or credentials.
  2. Ensure `.env` is ignored by git and only `.env.example` is committed.
  3. Ensure sensitive server configurations are never exposed via `NEXT_PUBLIC_` prefixes.
  4. Ensure input payloads are strictly validated before processing.
- **Expected Report:** Security checklist results and confirmation of zero credential exposure.

---

## 6. Data Quality Reviewer
- **Purpose:** Audits raw and processed datasets for schema consistency, timestamps, sampling intervals, and sensor anomalies.
- **Trigger:** Dataset ingestion, preprocessing scripts, and transformation pipelines (Phases 1 & 2).
- **Required Inputs:** Data inspection scripts, raw data summaries, statistical profiles.
- **Validation Tasks:**
  1. Verify timestamp monotonicity and identify gaps.
  2. Confirm 15-minute sampling interval (96 steps/24h) and document irregular intervals.
  3. Audit `SM_50cm` target for missingness, negative values, and physical plausibility.
  4. Check environmental covariates (rainfall, temperature, humidity, radiation).
- **Expected Report:** Data audit summary, missing value percentages, distribution statistics, and recommended cleaning steps.

---

## 7. ML Integrity Reviewer
- **Purpose:** Enforces scientific rigor, temporal leakage prevention, sequence alignment, and fair evaluation.
- **Trigger:** Preprocessing, feature selection, baseline implementation, model training, and evaluation (Phases 2-5).
- **Required Inputs:** Train/val/test splits, sequence generator code, evaluation scripts, metric calculation code.
- **Validation Tasks:**
  1. Confirm splits are strictly chronological (no shuffling across time).
  2. Verify scalers and imputers are fit strictly on training splits only.
  3. Verify input sequence time range ($t-T \dots t$) does not overlap target ($t+96$).
  4. Validate metric implementations (MAE, RMSE, R²) for mathematical correctness.
  5. Ensure comparison against Persistence baseline uses identical test observations.
- **Expected Report:** Leakage check confirmation, horizon alignment verification, and metric reproducibility log.

---

## 8. Frontend Reviewer
- **Purpose:** Ensures Next.js dashboard quality, type safety, responsive design, and chart accuracy.
- **Trigger:** Any modification in `frontend/` (Phase 7).
- **Required Inputs:** Next.js components, Tailwind styles, Recharts configurations.
- **Validation Tasks:**
  1. Verify strict TypeScript compliance (`tsc --noEmit`).
  2. Ensure responsive layouts (mobile, tablet, desktop).
  3. Verify chart axes, tooltips, and time formatting accurately represent 24h predictions.
  4. Verify all 4 UI states are implemented: loading, empty, validation error, server error.
- **Expected Report:** UI validation findings, accessibility checklist, and build status.

---

## 9. Backend Reviewer
- **Purpose:** Ensures FastAPI robustness, schema validation, model inference parity, and error handling.
- **Trigger:** Any modification in `backend/` (Phase 6).
- **Required Inputs:** FastAPI routes, Pydantic schemas, inference integration code.
- **Validation Tasks:**
  1. Verify model is loaded once at startup, never during individual prediction requests.
  2. Verify strict Pydantic payload validation for feature order, dimensions, and types.
  3. Verify inference parity: backend prediction matches direct model output within float tolerance ($< 10^{-5}$).
  4. Verify HTTP error codes (400 for bad input, 503 for uninitialized model).
- **Expected Report:** API validation results, parity test output, and route contract audit.

---

## 10. Integration Reviewer
- **Purpose:** Audits the end-to-end interface between Frontend, Backend, and ML models.
- **Trigger:** API contract updates, model handoff, and Phase 8 integration.
- **Required Inputs:** `docs/API_CONTRACT.md`, frontend API client, backend route definitions.
- **Validation Tasks:**
  1. Verify request and response payload schemas match identically across client and server.
  2. Verify CORS configurations allow secure communication.
  3. Verify forecast timestamp calculations and unit alignment.
  4. Verify graceful frontend behavior during backend service outages.
- **Expected Report:** End-to-end compatibility matrix and integration test results.

---

## 11. Documentation Reviewer
- **Purpose:** Maintains documentation synchronization with real code, decisions, and experiment metrics.
- **Trigger:** Any change affecting architecture, phase status, API contracts, or ML metrics.
- **Required Inputs:** `README.md`, `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/API_CONTRACT.md`, `docs/EXPERIMENTS.md`, `PROJECT_STATE.md`.
- **Validation Tasks:**
  1. Ensure no future phases are documented as completed.
  2. Verify all reported metrics correspond to real test runs.
  3. Ensure ADRs are written for significant architectural decisions.
  4. Ensure all file paths and symbols are accurately documented.
- **Expected Report:** Documentation audit summary and verification of file references.
