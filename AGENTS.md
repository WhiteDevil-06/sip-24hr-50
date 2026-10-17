# Agent Instruction & Governance System — Smart Irrigation Prediction

Welcome to the **Deep Learning-Based Soil Moisture Prediction for Smart Irrigation** repository.

This project enforces strict role-based development, phase gates, mandatory procedural review, and evidence-based engineering.

## 1. Mandatory Instruction Discovery Sequence
Every agent or developer beginning a session in this repository **MUST** read instructions in the following order before modifying or planning changes:
1. `README.md` (Project Context, Architecture, Team Roles)
2. `AGENTS.md` / `GEMINI.md` (This file — Antigravity entry point)
3. `.agent/README.md` (System design of the governance instructions)
4. `.agent/GLOBAL_RULES.md` (Rules A through M — binding on all team members and agents)
5. `.agent/PHASES.md` (Phase definitions, acceptance criteria, dependencies, phase gates)
6. `.agent/PROJECT_STATE.md` (Current active phase, ownership, verified environment, blockers)
7. `.agent/AGENT_REGISTRY.md` (Specialist review registry and procedural checklists)
8. `.agent/roles/README.md` (Role definitions and strict boundary rules)
9. Active Role instruction:
   - Check `.agent/ACTIVE_ROLE.local` if present (local developer override, git-ignored).
   - Otherwise check `.agent/ACTIVE_ROLE`.
   - Read `.agent/roles/<active-role>.md`.
10. Relevant subsystem rules in `.agent/rules/*.md`.
11. Relevant architecture, decision, and contract docs in `docs/`.

## 2. Tool & Subagent Reality Check
- **No Native Arbitrary Subagents:** In this coding environment, general autonomous subagents are not natively registered as executable tools.
- **Procedural Reviews:** All specialist reviews (Code Reviewer, Test Validator, Security, Data Quality, ML Integrity, Frontend, Backend, Integration, Documentation) must be executed as **explicit, documented procedural checklists**. Never report or pretend a self-review was an independent subagent execution.

## 3. Strict Ownership Boundaries
- **Project Lead (You / Me):** Owns AI/ML learning, data preprocessing, baseline, LSTM training, evaluation, model handoff artifact, and final integration. Guided step-by-step; never hand off unexplained bulk code.
- **Ram Charan (Website Developer):** Owns Next.js + Tailwind CSS + Recharts dashboard. Consumes approved API contract. Must never invent model outputs or metrics.
- **Rahul (Backend & Model-Serving Developer):** Owns FastAPI inference service. Loads saved trained model artifact without retraining. Strictly prohibited from retraining, altering architecture, or inventing predictions.

## 4. Phase Gate Protocol
- Never proceed past a phase boundary without explicit human approval from the Project Lead.
- Current active phase: **Phase 0 (Project & Agent-System Initialization)**.
- No code for preprocessing, LSTM, FastAPI, or Next.js may be implemented during Phase 0.
