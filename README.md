# Deep Learning-Based Soil Moisture Prediction for Smart Irrigation

## 1. Project Overview & Research Objective
This project develops an LSTM-based time-series model that predicts soil moisture at 50 cm depth (`SM_50cm`) 24 hours into the future (corresponding to 96 time steps at a 15-minute sampling interval).
The planned dataset is the **IISc Berambadi** soil/environmental dataset ([Zenodo record 22109968](https://zenodo.org/records/22109968)).

The research direction investigates whether selected or reduced environmental input configurations can achieve useful, actionable forecasting performance compared against a Persistence (Naïve) baseline.

The final software application will deliver:
- Historical soil moisture tracking and visualization.
- 24-hour predictive forecast curve.
- Side-by-side comparison of model configurations using actual verified evaluation metrics (MAE, RMSE, R²).
- Threshold-justified irrigation recommendations.
- Explicit communication of model limitations and uncertainty bounds.

> **Scope Boundary:** This is an academic research and software engineering project. Physical irrigation hardware, microcontrollers (ESP32), automatic pump actuations, and reinforcement learning are explicitly out of scope unless separately approved by the Project Lead.

---

## 2. Team Structure & Ownership Boundaries

| Role | Owner | Primary Responsibilities | Assigned Phases |
| :--- | :--- | :--- | :--- |
| **Role A: Project Lead & AI Developer** | You (Me) | Understands ML theory, implements data preprocessing, Persistence baseline, builds & trains PyTorch LSTM, evaluates metrics, creates model handoff package, comprehensive educational study report. | **Phases 0, 1, 2, 3, 4, 5 (COMPLETED)** |
| **Role B: Website Developer** | Ram Charan | Next.js (App Router), TypeScript, Tailwind CSS, Recharts dashboard, metrics display, responsive UI states. (Code ready in external repo, to be imported & tested). | **Phase 7 (Website Development)** |
| **Role C: Backend & Integration Developer** | Rahul | Python FastAPI serving service, loads saved model artifact, applies exact approved preprocessing, enforces request validation, ensures inference parity, E2E integration, and final demonstration. | **Phases 6, 8, 9 (Backend, Integration, Validation)** |

---

## 3. Technology Stack

- **AI & Preprocessing (Project Lead):** Python 3.13, PyTorch 2.14, NumPy, Pandas, scikit-learn, Pytest.
- **Backend Serving (Rahul):** Python 3.13, FastAPI, Pydantic, Uvicorn, Pytest.
- **Frontend Dashboard (Ram Charan):** Next.js (App Router), React, TypeScript (strict), Tailwind CSS, Recharts.
- **Engineering Quality:** Git, isolated virtual environment, strict phase gates, ADR documentation, typed API contracts.

---

## 4. Role Selection for Cloned Repositories

When team members clone this repository, they must select their active role without overwriting other members' git tracking.

### Step 1: Check Current Role
The default role in [.agent/ACTIVE_ROLE](file:///c:/Users/raksh/ANN/.agent/ACTIVE_ROLE) is `project-lead`.

### Step 2: Set Local Role (Recommended for Team Members)
Create a `.agent/ACTIVE_ROLE.local` file (this file is ignored by Git in `.gitignore`):
```bash
# For Website Developer (Ram Charan):
echo website-developer > .agent/ACTIVE_ROLE.local

# For Backend Developer (Rahul):
echo ai-backend-developer > .agent/ACTIVE_ROLE.local

# For Project Lead:
echo project-lead > .agent/ACTIVE_ROLE.local
```

### Supported Role Identifiers:
- `project-lead`
- `website-developer`
- `ai-backend-developer`

---

## 5. Phased Project Roadmap & Phase Gates

The project advances through 10 strictly gated phases. Advancing to the next phase requires explicit human sign-off from the Project Lead.

- **Phase 0:** Project and Agent-System Initialization *(APPROVED COMPLETE)*
- **Phase 1:** Dataset Audit *(APPROVED COMPLETE)*
- **Phase 2:** Preprocessing Pipeline *(APPROVED COMPLETE)*
- **Phase 3:** Persistence Baseline *(APPROVED COMPLETE)*
- **Phase 4:** LSTM Learning and Implementation *(APPROVED COMPLETE)*
- **Phase 5:** Experiments and Model Evaluation *(APPROVED COMPLETE)*
- **Phase 6:** Backend and Model Serving *(Active Phase — Rahul)*
- **Phase 7:** Website Development *(Ready for Import — Ram Charan)*
- **Phase 8:** Integration *(Rahul & Ram Charan)*
- **Phase 9:** Final Validation and Demonstration *(Rahul & Team)*

See [.agent/PHASES.md](file:///c:/Users/raksh/ANN/.agent/PHASES.md) and [.agent/PROJECT_STATE.md](file:///c:/Users/raksh/ANN/.agent/PROJECT_STATE.md) for full status.

---

## 6. Directory Structure

```
.
├── .agent/                    # Shared governance & instruction system
│   ├── ACTIVE_ROLE            # Default role definition
│   ├── ACTIVE_ROLE.example    # Local override template
│   ├── GLOBAL_RULES.md        # Binding rules A through M
│   ├── PHASES.md              # Phase definitions & acceptance criteria
│   ├── PROJECT_STATE.md       # Real-time state & verified environment
│   ├── AGENT_REGISTRY.md      # 11 specialist review personas & procedural checklists
│   ├── roles/                 # Role-specific responsibilities & boundaries
│   ├── agents/                # Specialist reviewer instructions
│   ├── workflows/             # Standard operating procedures
│   └── rules/                 # Domain-specific constraints
├── data/                      # Data directories (raw data git-ignored)
│   ├── raw/                   # Raw IISc Berambadi dataset (downloaded separately)
│   └── processed/             # Cleaned, chronologically split splits
├── backend/                   # FastAPI serving application (Phase 6)
├── frontend/                  # Next.js web dashboard (Phase 7)
├── docs/                      # Persistent project documentation
│   ├── ARCHITECTURE.md        # System architecture diagram & design
│   ├── DECISIONS.md           # Architecture Decision Records (ADRs)
│   ├── API_CONTRACT.md        # Frontend-backend inference contract
│   ├── VALIDATION.md          # Validation run log & test records
│   └── EXPERIMENTS.md         # ML baseline & experiment logs
├── tests/                     # Unit, integration, and ML integrity tests
├── AGENTS.md                  # Antigravity primary discovery instructions
├── GEMINI.md                  # Dual tool instructions pointer
└── README.md                  # This file
```
