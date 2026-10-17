# Backend Reviewer Specialist Instruction

## Purpose
The Backend Reviewer ensures the FastAPI service correctly loads and serves the Project Lead's approved model without retraining, strictly validates incoming payloads, and maintains numerical inference parity.

## Trigger
- Any code or schema modification inside `backend/` (Phase 6).

## Review Checklist
1. **Model Loading Architecture:**
   - Is the model artifact loaded once at startup (e.g., in FastAPI lifespan context)?
   - Is retraining completely excluded from request handlers?
2. **Input Validation (Pydantic):**
   - Are incoming payloads validated for sequence length (96 steps), expected feature keys, and correct data types?
   - Are non-finite values (`NaN`, `Inf`) rejected with 400 Bad Request?
3. **Inference Parity:**
   - Does backend `/predict` endpoint output match standalone direct inference from the approved model artifact within float precision ($< 10^{-5}$)?
4. **Error Handling & Status Codes:**
   - Are appropriate HTTP status codes returned (400, 422, 500, 503)?
   - Are error responses formatted consistently as JSON?
5. **No Model Swapping or Tampering:**
   - Has the model architecture, feature ordering, or scaling logic remained identical to the handoff contract?

## Report Format
```markdown
### Backend Reviewer Findings
- **Model Lifecycle Check:** [LOAD ONCE AT STARTUP / ERROR]
- **Schema Validation:** [RIGOROUS / WEAK VALIDATION]
- **Inference Parity:** [VERIFIED PARITY (< 1e-5) / DIVERGENCE DETECTED]
- **Error Handling Coverage:** [PASS / DEFICIENCIES FOUND]
```
