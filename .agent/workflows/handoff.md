# Workflow: Model Handoff Contract Protocol

This workflow defines the mandatory protocol for handing off the trained LSTM model artifact and preprocessing pipeline from the Project Lead (Role A) to Rahul (Role C).

## Step 1: Handoff Bundle Preparation (Project Lead)
The Project Lead must prepare and verify the following items:
1. **Model Artifact:** Serialized model file (e.g., `model.keras`) saved from the approved Phase 5 experiment.
2. **Preprocessing Artifacts:** Saved scaler and imputer objects (e.g., `scaler.pkl`) fit strictly on training data.
3. **Feature Schema:** Exact list of feature names and required ordering.
4. **Input Tensor Specification:** Expected input shape `[batch, sequence_length, n_features]` (e.g., `[1, 96, 5]`).
5. **Forecast Horizon:** Documented target timestamp ($t + 96$ steps / 24 hours).
6. **Scaling Factors:** Parameters required to inverse-transform raw model outputs back to physical moisture units ($m^3/m^3$ or %).
7. **Test Fixtures:** At least 3 sample input sequences with corresponding expected model output values for verification.

## Step 2: Contract Documentation
- Document the schema, endpoint paths, request formats, and response structures in `docs/API_CONTRACT.md`.

## Step 3: Handoff Verification (Rahul)
Before writing any FastAPI code, Rahul must inspect the bundle:
- Verify model loads without retraining.
- Run test fixtures and verify direct model outputs match expected numbers.
- If any artifact is missing or incomplete, report the blocker immediately. Rahul must NOT fabricate missing artifacts.

## Step 4: Approval & Transition
- Project Lead signs off on handoff integrity.
- Rahul initiates Phase 6 (`Backend and Model Serving`).
