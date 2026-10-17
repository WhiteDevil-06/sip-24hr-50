# Subsystem Rules: Backend & Model Serving (Rahul)

These rules apply to all API and model-serving code inside `backend/`.

## 1. Framework & Architecture
- Use **FastAPI** with **Pydantic** for typed request and response validation.
- Load the approved model artifact and preprocessing scalers strictly **once at application startup** (using FastAPI lifespan events).
- The server must never retrain the model or fit scalers during startup or in response to prediction requests.

## 2. API Schema Integrity
- All request and response models must be explicitly defined with Pydantic and documented in `docs/API_CONTRACT.md`.
- Enforce exact feature ordering, input shape `[batch, 96, n_features]`, and reject non-finite numbers (`NaN`, `Inf`) with 400 Bad Request.

## 3. Inference Parity Verification
- Automated tests must execute inference through the FastAPI endpoint and compare the result against direct invocation of the saved model artifact.
- Predictions must match within floating-point tolerance ($< 10^{-5}$).

## 4. Operational Health & Error Handling
- Implement `/health` endpoint returning server status and model loading state.
- Handle uninitialized model state gracefully with 503 Service Unavailable.
