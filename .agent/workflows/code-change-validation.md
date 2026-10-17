# Workflow: Code Change Validation & Specialist Reviews

Every meaningful code or configuration modification **MUST** trigger this validation workflow before being declared complete.

## Step 1: Specialist Selection
Identify the relevant specialists for the changed files:
- **General Code:** `code-reviewer`, `test-validator`
- **Data / Preprocessing:** `data-quality-reviewer`, `ml-integrity-reviewer`
- **Machine Learning / Training:** `ml-integrity-reviewer`, `code-reviewer`
- **Frontend / Next.js:** `frontend-reviewer`, `code-reviewer`
- **Backend / FastAPI:** `backend-reviewer`, `code-reviewer`, `security-reviewer`
- **API Contracts / Interfaces:** `integration-reviewer`, `documentation-reviewer`

## Step 2: Procedural Review Checklist
Execute each selected specialist review using the checklists defined in `.agent/agents/*.md`:
- Note that in this environment, reviews operate as procedural checklists.
- Document any findings, potential edge cases, or code smells.

## Step 3: Real Test Execution
- Run applicable unit tests, type checks, or build commands in the terminal via `run_command`.
- Capture exact commands, exit codes, and output logs.
- Never weaken assertions or mock results to force a pass.

## Step 4: Diff Inspection
- Run `git diff` or inspect changes.
- Ensure no accidental files, secrets, or temporary artifacts are staged.

## Step 5: Report Findings
- Include findings in the Session Report under Section D (Specialist Reviews) and Section E (Validation).
