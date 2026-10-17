# Team Roles & Ownership Governance

This directory defines the explicit responsibility boundaries and strict operational guidelines for each team member working in this repository.

## Ownership Matrix

| Role | Human Owner | Primary Files & Responsibilities | Strictly Prohibited Actions |
| :--- | :--- | :--- | :--- |
| **Role A: Project Lead, AI Developer & Integration Owner** | You (Me) | `data/`, ML preprocessing, Persistence baseline, LSTM architecture, model training, evaluation (`docs/EXPERIMENTS.md`), model handoff artifact, and final E2E integration. | Must not be given unexplained bulk code generation. Learning and deep conceptual understanding are mandatory. |
| **Role B: Website Developer** | Ram Charan | `frontend/`, Next.js components, Tailwind CSS, Recharts dashboard, client API consumption, UI states (loading, empty, error). | Prohibited from inventing model outputs, mock metrics as real, or modifying backend/ML code. |
| **Role C: Backend & Model-Serving Developer** | Rahul | `backend/`, FastAPI inference service, Pydantic validation, model loading without retraining, parity testing. | Prohibited from independently training primary model, replacing model, altering architecture/features, or faking metrics. |

## Role Switching Protocol
1. Each developer's active role is detected from `.agent/ACTIVE_ROLE.local` (local git-ignored file) or `.agent/ACTIVE_ROLE` (tracked default).
2. Cloned repositories default to `project-lead`.
3. When Ram Charan or Rahul clone the repo, they set their role by creating `.agent/ACTIVE_ROLE.local` containing `website-developer` or `ai-backend-developer`.
4. Any coding agent MUST read the active role file upon session start and enforce that role's boundaries strictly.
