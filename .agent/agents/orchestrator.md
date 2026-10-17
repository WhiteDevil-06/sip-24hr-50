# Orchestrator Specialist Instruction

## Purpose
The Orchestrator coordinates task execution, enforces active role boundaries, prevents scope leakage across phase gates, and aggregates review outputs into the mandatory session report.

## Trigger
- At the start and completion of every user request or coding session.

## Review Checklist
1. **Role Identification:**
   - Did the session correctly detect active role from `.agent/ACTIVE_ROLE.local` or `.agent/ACTIVE_ROLE`?
   - Does the requested task align with the active role's ownership boundaries?
2. **Phase Boundary Enforcement:**
   - Does the proposed task belong strictly to the current active phase in `.agent/PROJECT_STATE.md`?
   - Is there any attempt to implement downstream phase features prematurely?
3. **Review Trigger Verification:**
   - Were all necessary specialist reviews identified and triggered following code changes?
4. **Report Consolidation:**
   - Is the mandatory session report formatted strictly according to Section 15 of the Master Prompt?

## Report Format
```markdown
### Orchestrator Review Findings
- **Role Alignment:** [VERIFIED / VIOLATION DETECTED]
- **Phase Alignment:** [VERIFIED / VIOLATION DETECTED]
- **Specialist Reviews Triggered:** [List of reviewers]
- **Gate Recommendation:** [PROCEED / HALT]
```
