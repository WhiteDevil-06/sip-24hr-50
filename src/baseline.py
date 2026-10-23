"""
Phase 3: Naïve Persistence Baseline Forecasting
Mathematical Formulation: y_hat_{t+96} = y_t
Theoretical Rationale:
Time-series persistence assumes that soil moisture 24 hours into the future (96 steps)
will equal the current soil moisture. Because soil moisture at 50 cm depth has high
hydraulic and thermal inertia (autocorrelation r = 0.9141 at lag 96), persistence forms
an essential, highly competitive reference point that any deep learning model must beat.
"""

from typing import Dict, Tuple, Optional
import numpy as np
from src.metrics import compute_metrics


class NaivePersistenceBaseline:
    """
    Naïve Persistence Forecaster for 24-hour horizon (t + 96 steps).
    Outputs the most recent observed value of the target variable from the input sequence:
    y_hat_{t + 96} = X[t, -1, target_idx]
    """

    def __init__(self, target_idx: int = 0):
        self.target_idx = target_idx

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Generates persistence forecasts from input sequence tensor.
        Args:
            X: 3D numpy array of shape [N, window_size, n_features]
        Returns:
            1D numpy array of predictions of shape [N]
        """
        if X.ndim != 3:
            raise ValueError(f"Expected 3D tensor [N, window_size, n_features], got ndim={X.ndim}")
        # Latest observation in the sequence is at index -1
        return X[:, -1, self.target_idx].copy()

    def evaluate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        target_scaler=None,
    ) -> Tuple[Dict[str, float], np.ndarray]:
        """
        Evaluates persistence predictions against ground truth.
        If target_scaler is provided, inverts predictions and ground truth
        back to original physical units (% Volumetric Water Content) before computing metrics.

        Returns:
            metrics: Dict with 'mae', 'rmse', 'r2'
            y_pred_unscaled: 1D numpy array of unscaled predictions
        """
        y_pred = self.predict(X)

        if target_scaler is not None:
            # Reshape for sklearn scaler
            y_pred_unscaled = target_scaler.inverse_transform(y_pred.reshape(-1, 1)).flatten()
            y_true_unscaled = target_scaler.inverse_transform(y.reshape(-1, 1)).flatten()
        else:
            y_pred_unscaled = y_pred
            y_true_unscaled = y

        metrics = compute_metrics(y_true_unscaled, y_pred_unscaled)
        return metrics, y_pred_unscaled
