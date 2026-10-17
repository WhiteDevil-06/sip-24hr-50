# Integration Reviewer Specialist Instruction

## Purpose
The Integration Reviewer inspects end-to-end interface contracts, request/response payload synchronization, CORS headers, time formatting, and full-stack operational stability.

## Trigger
- Modifications to `docs/API_CONTRACT.md`, backend route interfaces, frontend API client code, or Phase 8 integration activities.

## Review Checklist
1. **Contract Synchronization:**
   - Do frontend TypeScript types match backend Pydantic schemas field-for-field?
2. **Payload & Prediction Consistency:**
   - Does the prediction value rendered on the frontend dashboard correspond exactly to the value computed by the backend?
3. **Time & Unit Alignment:**
   - Are timestamps correctly parsed across timezones (UTC vs. local IST)?
   - Are soil moisture units consistent (e.g., $m^3/m^3$ or %)?
4. **Resilience & Fault Tolerance:**
   - Does the frontend degrade gracefully when the backend server is stopped or unreachable?
   - Are CORS headers correctly configured to permit authorized origin communication without exposing open wildcard security vulnerabilities?

## Report Format
```markdown
### Integration Reviewer Findings
- **Contract Schema Parity:** [SYNCHRONIZED / MISMATCH DETECTED]
- **Value Consistency:** [EXACT MATCH / DIVERGENCE DETECTED]
- **Unit & Time Integrity:** [VERIFIED / ISSUES DETECTED]
- **Fault Handling:** [ROBUST / UNHANDLED EXCEPTION]
```
