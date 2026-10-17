# Frontend Reviewer Specialist Instruction

## Purpose
The Frontend Reviewer inspects Next.js application architecture, TypeScript type safety, responsive layout design, chart accuracy, and user interaction states.

## Trigger
- Any code or style modification inside `frontend/` (Phase 7).

## Review Checklist
1. **Type Safety & Build Cleanliness:**
   - Does TypeScript pass without errors (`npx tsc --noEmit`)?
   - Does Next.js build succeed without warnings or build errors (`npm run build`)?
2. **Component Architecture:**
   - Are components modular, readable, and properly decoupled?
   - Is Tailwind CSS used cleanly without arbitrary hardcoded inline styles?
3. **Chart Visualizations (Recharts):**
   - Do charts handle time-series dates/times accurately without off-by-one or timezone distortions?
   - Are axes, units, legends, and tooltips clearly labeled?
4. **Mandatory UI States:**
   - Are loading states (skeletons/spinners) implemented?
   - Are empty data states graceful and informative?
   - Are input validation errors communicated clearly?
   - Are server/connection errors handled cleanly without application crashes?
5. **No Fabricated Outputs:**
   - Are all displayed metrics and predictions sourced from verified backend responses or clearly marked `[MOCK]` during development?

## Report Format
```markdown
### Frontend Reviewer Findings
- **TypeScript Check:** [PASS / FAIL]
- **Build Verification:** [PASS / FAIL / NOT RUN]
- **UI States Check:** [COMPLETE / MISSING STATES]
- **Chart Accuracy:** [VERIFIED / ISSUES IDENTIFIED]
- **Accessibility & Responsiveness:** [VERIFIED / NEEDS ATTENTION]
```
