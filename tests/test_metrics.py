"""
Unit tests for evaluation metrics (MAE, RMSE, R^2)
"""

import numpy as np
import pytest
from src.metrics import compute_metrics


def test_perfect_prediction():
    y_true = np.array([10.0, 15.0, 20.0, 25.0])
    y_pred = np.array([10.0, 15.0, 20.0, 25.0])
    metrics = compute_metrics(y_true, y_pred)

    assert metrics["mae"] == 0.0
    assert metrics["rmse"] == 0.0
    assert metrics["r2"] == 1.0


def test_known_metrics_calculation():
    y_true = np.array([10.0, 20.0])
    y_pred = np.array([12.0, 18.0]) # errors: +2, -2
    metrics = compute_metrics(y_true, y_pred)

    assert metrics["mae"] == 2.0
    assert metrics["rmse"] == 2.0
    # Mean of y_true is 15. ss_tot = (10-15)^2 + (20-15)^2 = 25 + 25 = 50.
    # ss_res = (10-12)^2 + (20-18)^2 = 4 + 4 = 8.
    # R2 = 1 - 8/50 = 1 - 0.16 = 0.84.
    assert metrics["r2"] == 0.84


def test_length_mismatch_raises():
    with pytest.raises(ValueError):
        compute_metrics(np.array([1.0, 2.0]), np.array([1.0]))
