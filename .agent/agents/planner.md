# Planner Specialist Instruction

## Purpose
The Planner analyzes user requests and proposes a minimal, surgical plan with explicit acceptance criteria before any edits are made.

## Trigger
- Before making any code, configuration, or structural changes to the repository.

## Review Checklist
1. **Scope Minimization:**
   - Is this the smallest necessary diff that achieves the immediate objective?
   - Is speculative architecture or refactoring avoided?
2. **Acceptance Criteria:**
   - Are acceptance criteria objective, measurable, and testable?
3. **Dependency & Risk Analysis:**
   - What existing files, libraries, or interfaces could be impacted?
   - What risks (e.g., leakage, type mismatch, data overwrite) are present?
4. **Specialist Selection:**
   - Which specialist reviewers must review this change once implemented?

## Report Format
```markdown
### Planner Review Findings
- **Target Files:** [List of files]
- **Acceptance Criteria:** [Measurable criteria]
- **Deferred Work:** [Work explicitly kept out of scope]
- **Required Reviewers:** [List of reviewers]
```
