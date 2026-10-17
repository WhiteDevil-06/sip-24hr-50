# Workflow: Session Start & Instruction Discovery

Every coding session in this repository **MUST** follow this exact startup procedure before attempting any planning or modifications.

## Step 1: Instruction Discovery Sequence
Read the following files in strict order:
1. `README.md`
2. `AGENTS.md` (and `GEMINI.md`)
3. `.agent/README.md`
4. `.agent/GLOBAL_RULES.md`
5. `.agent/PHASES.md`
6. `.agent/PROJECT_STATE.md`
7. `.agent/AGENT_REGISTRY.md`
8. `.agent/roles/README.md`
9. Active Role file:
   - Check if `.agent/ACTIVE_ROLE.local` exists. If present, read the role name from it.
   - If not, read `.agent/ACTIVE_ROLE`.
   - Read `.agent/roles/<active-role>.md`.
10. Relevant subsystem rules in `.agent/rules/*.md`.
11. Relevant docs in `docs/` (`ARCHITECTURE.md`, `DECISIONS.md`, `API_CONTRACT.md`, `VALIDATION.md`, `EXPERIMENTS.md`).

## Step 2: Environment & Git Inspection
Execute non-destructive inspection commands:
1. Check Git status: `git status` (confirm branch, uncommitted work).
2. Check active directory: `pwd` / `cd`.
3. Check tools if not already verified (Python, Node, npm).
4. Inspect any relevant files associated with the active phase.

## Step 3: Role & Phase Alignment Check
1. Verify that the requested task is owned by the detected active role.
2. Verify that the requested task belongs strictly to the active phase in `.agent/PROJECT_STATE.md`.
3. If there is any discrepancy between user instruction and active role/phase, pause and explicitly request clarification from the Project Lead.
