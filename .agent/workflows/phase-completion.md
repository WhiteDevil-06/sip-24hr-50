# Workflow: Phase Completion & Human Approval Gate

Every phase transition in this project is strictly gated. Advancing to the next phase requires explicit human sign-off from the Project Lead.

## Step 1: Acceptance Criteria Audit
- Verify every acceptance criterion listed in `.agent/PHASES.md` for the current phase.
- Gather concrete evidence (test outputs, execution logs, diff review).

## Step 2: Documentation & ADR Audit
- Verify that `docs/DECISIONS.md`, `docs/VALIDATION.md`, and `docs/EXPERIMENTS.md` are completely updated.
- Verify that all code changes are committed or cleanly staged without unstaged residue.

## Step 3: Formal Phase Gate Submission
- Set Phase Status in `.agent/PROJECT_STATE.md` to:
  `VALIDATED — AWAITING HUMAN APPROVAL`
- Submit the Phase Gate report to the Project Lead containing:
  1. Summary of completed work.
  2. Concrete evidence and validation outputs.
  3. Identified limitations or deferred items.
  4. Specific request for Project Lead approval to transition to the next phase.

## Step 4: Stop and Wait
- **STOP.** Do not begin work on the next phase.
- Wait for explicit written approval from the Project Lead.
- Once approved, update status to `APPROVED COMPLETE`, set the next phase to `IN PROGRESS`, and update `PROJECT_STATE.md`.
