# Subsystem Rules: Data & ML Scientific Integrity

These rules enforce strict scientific standards to prevent temporal leakage, ensure reproducibility, and maintain fair comparative evaluation.

## 1. Zero Temporal Leakage
- **Chronological Splitting:** Train, validation, and test datasets must be partitioned strictly by chronological timestamp (e.g., Train: 2018-2019, Val: early 2020, Test: late 2020). Random or k-fold shuffling across time is strictly prohibited.
- **Scaler Isolation:** Scalers (`MinMaxScaler`, `StandardScaler`) and imputers must be fitted **exclusively on the training partition**. Transform operations alone are applied to validation and test sets.
- **Lookahead Prevention:** Input features must not contain data from future time steps.

## 2. Forecast Horizon Alignment
- Target variable is `SM_50cm` at time $t + 96$ (24 hours ahead at 15-minute sampling frequency).
- Timestamp alignment between input feature tensors and target vectors must be verified via unit tests.

## 3. Evaluation Fairness
- Baseline Persistence model and LSTM models must be evaluated on the **exact same held-out test observations**.
- All metrics (MAE, RMSE, R²) must be evaluated on original physical moisture units ($m^3/m^3$ or %) after proper inverse scaling.
- Novelty claims are prohibited until relevant literature is reviewed and supported by rigorous empirical results.
