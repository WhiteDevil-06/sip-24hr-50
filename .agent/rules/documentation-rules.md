# Subsystem Rules: Documentation Governance

These rules govern the accuracy, structure, and maintenance of all project documentation.

## 1. Documentation Structure
- `README.md`: High-level overview, quickstart, role selection, architecture summary.
- `docs/ARCHITECTURE.md`: Technical system architecture, component diagrams, data flows.
- `docs/DECISIONS.md`: Architecture Decision Records (ADRs) tracking significant design choices.
- `docs/API_CONTRACT.md`: Living API contract between frontend and backend.
- `docs/VALIDATION.md`: Historical validation records, commands, and outputs.
- `docs/EXPERIMENTS.md`: Machine learning experiment log, hyperparameters, split dates, and metrics.
- `.agent/PHASES.md`: Phase definitions and acceptance criteria.
- `.agent/PROJECT_STATE.md`: Real-time active phase tracker and verified facts.

## 2. Integrity & Truthfulness
- Documentation must accurately reflect the code as it exists today. Never describe future planned features as completed.
- Every reported metric (MAE, RMSE, R²) in `docs/EXPERIMENTS.md` must link to an actual test execution log.
- All file links must use GitHub-style markdown syntax `[filename](file:///path/to/file)`.
