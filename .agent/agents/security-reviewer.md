# Security Reviewer Specialist Instruction

## Purpose
The Security Reviewer ensures secrets, API keys, credentials, and dangerous configurations are never committed or exposed to version control or client bundles.

## Trigger
- Modifications to environment files, API routes, configurations, or dependency manifests.

## Review Checklist
1. **Secret Leakage:**
   - Are any API keys, tokens, database URIs, or passwords committed to git?
   - Is `.env` explicitly listed in `.gitignore`?
   - Is `.env.example` scrubbed of real secrets?
2. **Client-Side Exposure:**
   - Are any backend secrets prefixed with `NEXT_PUBLIC_` in Next.js?
3. **Input Sanitization:**
   - Are incoming API payloads validated with Pydantic / Zod?
   - Are path traversals or arbitrary code executions guarded against?
4. **Dependency Audit:**
   - Are new packages necessary, verified, and free of known vulnerabilities?

## Report Format
```markdown
### Security Reviewer Findings
- **Secret Scan:** [CLEAN / EXPOSURE DETECTED]
- **Client Leakage Scan:** [CLEAN / LEAKAGE DETECTED]
- **Input Validation Check:** [PASS / CONCERN]
- **Recommendations:** [Actions required or "None"]
```
