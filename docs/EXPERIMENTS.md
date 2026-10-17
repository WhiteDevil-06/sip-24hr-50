# Machine Learning Experiments & Benchmark Registry

This document records all baseline and model training runs, dataset configurations, hyperparameter settings, and verified evaluation metrics.

> [!IMPORTANT]
> **Scientific Honesty Rule:**
> In accordance with Rule A, Rule E, and Rule G of the Global Rules, no metrics, benchmarks, or novelty claims may be recorded in this document without direct empirical test logs from code execution. Speculative or invented metrics are strictly prohibited.

---

## Benchmark Metrics Table

| Experiment ID | Model Description | Input Features | Sequence Window | Forecast Horizon | Split Dates (Train / Val / Test) | Test MAE | Test RMSE | Test R² | Date Run |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| *EXP-000 (Pending)* | *Persistence (Naïve) Baseline* | `SM_50cm(t)` | 1 step ($t$) | 24h ($t+96$) | *Pending Phase 1 Split* | — | — | — | *Phase 3* |
| *EXP-001 (Pending)* | *Univariate LSTM* | `SM_50cm(t-T...t)` | 96 steps (24h) | 24h ($t+96$) | *Pending Phase 1 Split* | — | — | — | *Phase 4* |
| *EXP-002 (Pending)* | *Multivariate LSTM* | `SM_50cm` + Climate | 96 steps (24h) | 24h ($t+96$) | *Pending Phase 1 Split* | — | — | — | *Phase 5* |
| *EXP-003 (Pending)* | *Reduced Feature LSTM* | Selected Covariates | 96 steps (24h) | 24h ($t+96$) | *Pending Phase 1 Split* | — | — | — | *Phase 5* |

---

## Experiment Detail Templates

### Baseline Specification (Phase 3 Target)
- **Mathematical Formula:** $\hat{y}_{t+96} = y_t$
- **Theoretical Rationale:** Time-series persistence assumes the soil moisture 24 hours into the future will equal the soil moisture at the current timestamp. Because soil moisture dynamics at 50 cm depth exhibit high thermal and hydraulic inertia, persistence forms a challenging and essential baseline that any deep learning model must convincingly outperform.

### LSTM Specification (Phase 4 Target)
- **Architecture:** Sequential LSTM (`InputLayer` -> `LSTM(units)` -> `Dropout` -> `Dense(1)`).
- **Target Variable:** `SM_50cm` at time $t + 96$ (15-minute interval).
- **Loss Function:** Mean Squared Error (MSE).
- **Evaluation Metrics:** Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), Coefficient of Determination ($R^2$).
