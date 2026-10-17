# Workflow: Bug Fix & Defect Remediation

This workflow establishes a disciplined approach to diagnosing, fixing, and preventing regressions when defects occur.

## Step 1: Defect Reproduction
- Recreate the failure with a minimal, deterministic reproduction script or failing unit test.
- Document exact error messages, traceback, and environment state.

## Step 2: Root Cause Analysis (RCA)
- Identify why the failure occurred (e.g., temporal leakage, missing scaler inverse transform, unhandled null timestamp, type mismatch).
- Determine if the issue is localized or affects broader architecture.

## Step 3: Targeted Remediation
- Implement the minimal fix addressing the root cause.
- Avoid broad refactorings while fixing defects.

## Step 4: Regression Prevention
- Add a permanent automated test covering the failure scenario to prevent regressions.
- Run the full test suite to verify no existing functionality was broken.
- Document the defect and resolution in `docs/DECISIONS.md` if it represents an architectural lesson.
