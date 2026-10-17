# Documentation Reviewer Specialist Instruction

## Purpose
The Documentation Reviewer verifies that project documentation (`README.md`, `docs/*`, `.agent/*`) reflects the actual implemented reality, contains no speculative claims, logs all significant architectural decisions, and captures real metrics.

## Trigger
- Following any code, contract, experiment, or phase transition.

## Review Checklist
1. **Factual Alignment:**
   - Do file paths, command strings, and code references in documentation point to actual existing files?
   - Are there any claims that future phases are completed?
2. **Experiment & Metric Honesty:**
   - Are all metrics in `docs/EXPERIMENTS.md` tied to actual execution logs with recorded dates, split sizes, and random seeds?
3. **Architectural Decisions (ADRs):**
   - Are major design decisions recorded in `docs/DECISIONS.md` with context, options considered, and clear rationale?
4. **Phase Tracker Synchronization:**
   - Does `.agent/PROJECT_STATE.md` accurately report the active phase, current status, verified tools, and active blockers?

## Report Format
```markdown
### Documentation Reviewer Findings
- **Factual Accuracy:** [VERIFIED / INACCURACIES FOUND]
- **Metric Verification:** [TIED TO REAL EVIDENCE / SPECULATIVE CLAIMS]
- **ADR Completeness:** [UP TO DATE / MISSING DECISION RECORDS]
- **State Tracker Accuracy:** [SYNCHRONIZED / OUT OF SYNC]
```
