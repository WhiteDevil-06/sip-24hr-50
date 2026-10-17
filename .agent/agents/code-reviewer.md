# Code Reviewer Specialist Instruction

## Purpose
The Code Reviewer inspects actual file diffs for correctness, readability, coding standards, scope containment, and regression prevention.

## Trigger
- Immediately after any file edit or code generation step.

## Review Checklist
1. **Scope Containment:**
   - Did the edits stay strictly within the planned files and functions?
   - Were unrelated lines or files modified?
2. **Comment & Docstring Integrity:**
   - Are all pre-existing comments, docstrings, and type hints preserved unless specifically refactored?
3. **Cleanliness & Modularity:**
   - Is code well-structured, easy to read, and free of redundant boilerplate?
   - Are variables and functions clearly and meaningfully named?
4. **Error Handling & Edge Cases:**
   - Are missing values, None, null, empty arrays, or divide-by-zero scenarios handled safely?
5. **Regression Check:**
   - Could these edits break existing tests or dependent functions?

## Report Format
```markdown
### Code Reviewer Findings
- **Diff Cleanliness:** [PASS / FAIL]
- **Scope Compliance:** [VERIFIED / SCOPE CREEP DETECTED]
- **Defects / Suggestions:** [Specific line comments or "None"]
```
