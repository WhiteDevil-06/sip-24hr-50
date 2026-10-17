# Role C: Backend and Model-Serving Developer

- **Owner:** Rahul
- **Role Identifier:** `ai-backend-developer`
- **Reference Files:**
  - [.agent/GLOBAL_RULES.md](file:///c:/Users/raksh/ANN/.agent/GLOBAL_RULES.md)
  - [.agent/PHASES.md](file:///c:/Users/raksh/ANN/.agent/PHASES.md) (Phase 6 Focus)
  - [.agent/PROJECT_STATE.md](file:///c:/Users/raksh/ANN/.agent/PROJECT_STATE.md)
  - [docs/API_CONTRACT.md](file:///c:/Users/raksh/ANN/docs/API_CONTRACT.md)

---

## 1. Responsibilities & Scope

- Build the Python **FastAPI** backend in `backend/`.
- Load and serve the approved model artifact trained by the Project Lead.
- Load the model and preprocessing artifacts strictly once at application startup.
- Connect API prediction requests to the loaded model's inference pipeline.
- Enforce strict request payload validation with **Pydantic**:
  - Verify sequence lengths, feature ordering, timestamp monotonicity, and data types.
- Apply the exact approved preprocessing transformations (scalers, imputers) provided in the handoff contract.
- Return typed, documented prediction responses matching the API contract.
- Implement `/health` and status endpoints.
- Handle invalid requests, non-finite values, and internal exceptions gracefully with appropriate HTTP status codes (e.g., 400 for bad input, 503 for uninitialized model).
- Write automated tests verifying that backend inference matches direct inference from the approved saved model artifact within float precision ($< 10^{-5}$).

---

## 2. Model Handoff Contract Protocol
Before beginning backend implementation, Rahul must verify the existence and integrity of:
1. Approved trained model artifact file (e.g., `.keras` or `.h5`).
2. Preprocessing scalers/artifacts or exact approved preprocessing code.
3. Feature names, ordering, and input sequence shape (e.g., `[batch, 96, n_features]`).
4. Forecast horizon definition ($t+96$).
5. Scaling and inverse-scaling parameters.
6. A set of approved input/output test fixtures for parity verification.

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
