# Global Rules — Core Behavioral Governance

These rules are unconditionally binding on every role (Project Lead, Ram Charan, Rahul) and every coding agent operating within this repository.

---

### Rule A — Evidence Over Assumptions
Never invent files, dataset properties, test results, research claims, model metrics, or tool capabilities.
Every statement must be strictly labeled as:
- **Verified:** Directly observed through execution or file inspection.
- **Assumed:** Working hypothesis requiring empirical validation.
- **Proposed:** A planned design or change not yet executed.
- **Unknown:** State or metric that has not yet been measured or observed.

### Rule B — Inspect Before Editing
Always inspect existing files, dependencies, environment state, and Git status before making any modifications.
Preserve uncommitted work and unrelated user modifications.

### Rule C — Small, Scoped Changes
Implement only the approved task for the current active phase. Avoid unrelated refactoring, speculative architecture, and premature implementation of downstream phases.

### Rule D — Mandatory Validation
Every meaningful code or configuration change must trigger appropriate specialist reviews and real execution of applicable tests, builds, or static checks.

### Rule E — No False Success Claims
Report the exact commands executed and their actual stdout/stderr outcomes.
Never report that an unexecuted test passed. If a test was not run, report it as `NOT RUN`. If blocked, report `BLOCKED`.

### Rule F — Preserve Data
Never overwrite raw dataset files (`data/raw/`).
Never remove samples silently without documented criteria and scientific justification.
Never perform destructive file operations without explicit authorization.

### Rule G — Scientific Reproducibility
Document all relevant dependencies, random seeds, software versions, hyperparameters, dataset periods, split dates, and validation results in `docs/EXPERIMENTS.md` and `docs/DECISIONS.md`.

### Rule H — Time-Series Integrity
Prevent all forms of data leakage:
- Split train, validation, and test sets strictly chronologically. Never use random shuffling for time-series splits.
- Fit scalers, imputers, and transformers strictly on training sets only.
- Ensure input sequence timestamps strictly precede the target forecast horizon.
- Maintain rigorous 24-hour horizon alignment (96 time steps at 15-minute intervals).

### Rule I — Security & Secret Safety
Never commit credentials, API keys, tokens, or environment files (`.env`, `.env.local`).
Never expose private server configuration to browser-accessible variables (e.g., `NEXT_PUBLIC_`).
Validate all incoming API payloads and sanitize inputs.

### Rule J — Human Approval Gate
Only the Project Lead can approve a phase as complete.
Never automatically begin a downstream phase without explicit written human authorization.

### Rule K — Tool Honesty & Subagent Reality
Verify tool, subagent, and workflow capabilities before relying on them.
When native subagents are unavailable, run specialist instructions as procedural checklists and explicitly report this procedural limitation. Never label an agent self-review as an independent subagent execution.

### Rule L — No Silent Scope Changes
Obtain explicit human approval before materially altering:
- The research objective (predicting `SM_50cm` 24h into the future).
- The dataset source (IISc Berambadi).
- The core model architecture (LSTM).
- The backend serving contract or frontend dashboard scope.
- Team ownership boundaries.

### Rule M — Preserve the Project Lead's Learning Process
During AI and model development phases, the coding assistant must teach, guide, and explain concepts step-by-step.
Do not generate large unexplained blocks of code. Enable the Project Lead to understand, inspect, validate, and academically defend every design decision and line of code.
