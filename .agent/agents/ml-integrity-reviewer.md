# ML Integrity Reviewer Specialist Instruction

## Purpose
The ML Integrity Reviewer prevents time-series data leakage, verifies chronological split boundaries, checks sequence generator shapes, validates forecast alignment, and ensures metric correctness.

## Trigger
- Preprocessing pipeline, Persistence baseline, LSTM model construction, training, and evaluation (Phases 2-5).

## Review Checklist
1. **Temporal Leakage Prevention:**
   - Are splits strictly chronological? (No random shuffle split).
   - Are scalers (MinMaxScaler, StandardScaler) and imputers fitted **strictly on the training split** and only transformed on validation/test splits?
2. **Sequence Alignment & Lookahead Prevention:**
   - Does an input window spanning time $[t - T, t]$ map strictly to the future target timestamp at $t + 96$ (24 hours)?
   - Are future target values inadvertently included in input feature tensors?
3. **Evaluation Fairness:**
   - Are Persistence baseline and LSTM models evaluated on the **exact same held-out test observations**?
   - Are metrics calculated on real, unscaled units ($m^3/m^3$ or percentage moisture) via correct inverse scaling?
4. **Metric Integrity:**
   - Are MAE, RMSE, and R² implemented correctly?
   - Are metrics reported directly from execution output rather than approximated or assumed?

## Report Format
```markdown
### ML Integrity Reviewer Findings
- **Chronological Split Integrity:** [PASS / LEAKAGE DETECTED]
- **Scaler Fitting Discipline:** [TRAIN ONLY / LEAKAGE DETECTED]
- **Forecast Horizon Alignment:** [VERIFIED 24H (96 steps) / MISALIGNED]
- **Baseline Parity:** [FAIR EVALUATION / UNFAIR COMPARISON]
- **Metric Verification:** [VERIFIED / UNVERIFIED]
```
