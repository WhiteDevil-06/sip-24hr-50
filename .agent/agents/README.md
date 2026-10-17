# Specialist Agent Review Instructions

This directory contains the operational specifications, review checklists, and reporting standards for all 11 specialist reviewer personas.

## Execution Reality & Protocol
In this Antigravity IDE environment, autonomous subagents are not registered as standalone background tools for code review.
Therefore, per **Rule K** and **Section 8**:
- Each specialist review must be executed as an **explicit procedural review checklist**.
- When reporting review results, the agent must clearly distinguish whether a review was:
  1. `Executed as a native subagent` (if native tool is verified and invoked).
  2. `Completed as a procedural checklist` (the standard operational mode here).
  3. `Not required, with reason` (e.g., frontend reviewer not triggered for Python data script).
  4. `Blocked or not run, with reason` (e.g., missing dependencies).
- The agent must **never claim or imply** that its self-review was an independent subagent execution.

## Review Personas Summary
1. [orchestrator.md](file:///c:/Users/raksh/ANN/.agent/agents/orchestrator.md) — Task lifecycle, role enforcement, report consolidation.
2. [planner.md](file:///c:/Users/raksh/ANN/.agent/agents/planner.md) — Scope definition, minimal diff planning, risk assessment.
3. [code-reviewer.md](file:///c:/Users/raksh/ANN/.agent/agents/code-reviewer.md) — Diff review, style standards, regression prevention.
4. [test-validator.md](file:///c:/Users/raksh/ANN/.agent/agents/test-validator.md) — Test runner execution, type checks, build checks.
5. [security-reviewer.md](file:///c:/Users/raksh/ANN/.agent/agents/security-reviewer.md) — Secrets, inputs, dependency safety.
6. [data-quality-reviewer.md](file:///c:/Users/raksh/ANN/.agent/agents/data-quality-reviewer.md) — Timestamps, sensor data, missingness.
7. [ml-integrity-reviewer.md](file:///c:/Users/raksh/ANN/.agent/agents/ml-integrity-reviewer.md) — Leakage, scaling, horizon alignment, metrics.
8. [frontend-reviewer.md](file:///c:/Users/raksh/ANN/.agent/agents/frontend-reviewer.md) — Next.js, TypeScript, Recharts, UI states.
9. [backend-reviewer.md](file:///c:/Users/raksh/ANN/.agent/agents/backend-reviewer.md) — FastAPI, Pydantic, inference parity, errors.
10. [integration-reviewer.md](file:///c:/Users/raksh/ANN/.agent/agents/integration-reviewer.md) — End-to-end interface and contract compliance.
11. [documentation-reviewer.md](file:///c:/Users/raksh/ANN/.agent/agents/documentation-reviewer.md) — Synchronization of docs, ADRs, and metrics.
