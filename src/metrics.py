"""
Standardized Evaluation Metrics for Soil Moisture Time-Series Forecasting
Computes:
1. Mean Absolute Error (MAE): Average absolute prediction deviation.
2. Root Mean Squared Error (RMSE): Square root of mean squared error (penalizes large misses).
3. Coefficient of Determination (R^2): Proportion of variance explained by the model.
"""

from typing import Dict
import numpy as np


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """
    Computes MAE, RMSE, and R2 between ground truth and predicted values.
    Accepts 1D numpy arrays.
    """
    y_true = np.asarray(y_true, dtype=np.float64).flatten()
    y_pred = np.asarray(y_pred, dtype=np.float64).flatten()

    if len(y_true) != len(y_pred):
        raise ValueError(f"Length mismatch: y_true has {len(y_true)}, y_pred has {len(y_pred)}")

    # Remove non-finite pairs if any
    valid_mask = np.isfinite(y_true) & np.isfinite(y_pred)
    y_t = y_true[valid_mask]
    y_p = y_pred[valid_mask]

    n = len(y_t)
    if n == 0:
        return {"mae": float("nan"), "rmse": float("nan"), "r2": float("nan")}

    # MAE
    mae = float(np.mean(np.abs(y_t - y_p)))

    # RMSE
    mse = float(np.mean((y_t - y_p) ** 2))
    rmse = float(np.sqrt(mse))

    # R^2
    ss_tot = float(np.sum((y_t - np.mean(y_t)) ** 2))
    ss_res = float(np.sum((y_t - y_p) ** 2))
    r2 = float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2": round(r2, 4),
    }
