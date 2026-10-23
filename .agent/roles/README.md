# Team Roles & Ownership Governance

This directory defines the explicit responsibility boundaries and strict operational guidelines for each team member working in this repository.

## Ownership Matrix

| Role | Human Owner | Primary Files & Responsibilities | Assigned Phases |
| :--- | :--- | :--- | :--- |
| **Role A: Project Lead & AI Developer** | You (Me) | Preprocessing pipeline, Persistence baseline, LSTM architecture, model training, evaluation (`docs/EXPERIMENTS.md`), model handoff bundle, and educational documentation. | **Phases 0, 1, 2, 3, 4, 5 (COMPLETED)** |
| **Role B: Website Developer** | Ram Charan | `frontend/`, Next.js components, Tailwind CSS, Recharts dashboard, client API consumption, UI states (loading, empty, error). Completed in external repository to be imported and tested. | **Phase 7 (Website Development)** |
| **Role C: Backend, Integration & Delivery Developer** | Rahul | `backend/`, FastAPI inference service, Pydantic validation, model loading without retraining, numerical parity testing, E2E frontend-backend integration, and final demonstration. | **Phases 6, 8, 9 (Backend, Integration, Final Validation)** |

## Role Switching Protocol
1. Each developer's active role is detected from `.agent/ACTIVE_ROLE.local` (local git-ignored file) or `.agent/ACTIVE_ROLE` (tracked default).
2. Cloned repositories default to `project-lead`.
3. When Ram Charan or Rahul clone the repo, they set their role by creating `.agent/ACTIVE_ROLE.local` containing `website-developer` or `ai-backend-developer`.
4. Any coding agent MUST read the active role file upon session start and enforce that role's boundaries strictly.
