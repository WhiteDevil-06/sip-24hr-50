# Role C: Backend and Model-Serving Developer

- **Owner:** Rahul
- **Role Identifier:** `ai-backend-developer`
- **Assigned Phases:**
  - **Phase 6:** Backend & Model Serving (FastAPI Service)
  - **Phase 8:** Integration (Connecting Frontend and Backend, CORS, E2E Request/Response verification)
  - **Phase 9:** Final Validation & Demonstration (Comprehensive testing, final system validation)
- **Reference Files:**
  - [.agent/GLOBAL_RULES.md](file:///c:/Users/raksh/ANN/.agent/GLOBAL_RULES.md)
  - [.agent/PHASES.md](file:///c:/Users/raksh/ANN/.agent/PHASES.md) (Phases 6, 8, 9 Focus)
  - [.agent/PROJECT_STATE.md](file:///c:/Users/raksh/ANN/.agent/PROJECT_STATE.md)
  - [docs/API_CONTRACT.md](file:///c:/Users/raksh/ANN/docs/API_CONTRACT.md) (Frozen Contract)
  - [models/model_metadata.json](file:///c:/Users/raksh/ANN/models/model_metadata.json) (Handoff Metadata)
  - [scripts/verify_handoff.py](file:///c:/Users/raksh/ANN/scripts/verify_handoff.py) (Handoff Test Script)

---

## 1. Responsibilities & Scope

### Phase 6: FastAPI Backend & Model Serving
- Build the Python **FastAPI** backend in `backend/`.
- Load the approved model artifact (`models/best_model.pt`) and scalers strictly once at application startup using lifespan context manager.
- Implement `/health`, `/api/v1/predict`, and `/api/v1/metrics` endpoints per `docs/API_CONTRACT.md`.
- Enforce strict request payload validation with **Pydantic**:
  - Verify sequence lengths (exactly 96 steps), feature ordering (5 features), timestamp monotonicity, and finite float values.
- Apply the exact approved preprocessing transformations (`models/scaler_metadata.json` or `feature_scaler.pkl`).
- Return typed, documented prediction responses matching the API contract.
- Write automated tests verifying that backend inference matches direct PyTorch inference within float precision ($< 10^{-5}$).

### Phase 8: End-to-End Integration
- Connect Next.js frontend (`frontend/`) to FastAPI backend (`backend/`) via environment variables (`NEXT_PUBLIC_API_URL`).
- Configure CORS, verify low latency ($< 150 \text{ ms}$), and validate live request/response data rendering.
- Verify that displayed predictions on the dashboard match backend inference exactly.

### Phase 9: Final Validation & Demonstration
- Run automated unit and integration tests across ML, backend, and frontend.
- Validate system reliability under offline, malformed, and edge-case network inputs.
- Ensure all technical documentation is aligned for final demonstration.

---

## 2. Model Handoff Contract Protocol
Before beginning backend implementation, Rahul must verify the existence and integrity of:
1. Approved trained model artifact file (`models/best_model.pt` PyTorch model weights).
2. Preprocessing scalers and artifacts (`models/feature_scaler.pkl`, `models/target_scaler.pkl`, and `models/scaler_metadata.json`).
3. Feature names, ordering, and input sequence shape (verified: `[batch, 96, 5]` features: `SM_50cm`, `Rainfall`, `Air_Temp`, `RH`, `Solar_Rad`).
4. Forecast horizon definition ($t+96$ = 24 hours ahead at 15-minute intervals).
5. Scaling and inverse-scaling parameters (frozen in `models/scaler_metadata.json` and `docs/API_CONTRACT.md`).
6. Approved input/output test fixtures for parity verification (validated by `scripts/verify_handoff.py`).

If any handoff artifact is missing or incomplete, Rahul must report the blocker rather than inventing artifacts or parameters.

---

## 3. Strict Prohibitions
Unless explicitly approved in writing by the Project Lead:
- **No Model Training:** Rahul must NOT independently train or retrain the primary LSTM model.
- **No Model Swapping:** Must NOT replace the approved model with another model or heuristic.
- **No Retraining on Request:** The server must NOT retrain the model on server startup or when prediction requests arrive.
- **No Architecture Changes:** Must NOT alter the model architecture, target variable, or forecast horizon.
- **No Feature Alterations:** Must NOT alter feature selection, ordering, or scaling parameters.
- **No Fabricating Predictions:** Must never invent prediction outputs or metrics when inference fails.
- **Mock Model Rules:** Rahul may create inference tests and clearly labeled mock fixtures for testing server plumbing, but must never present a mock fixture as the trained research model.
