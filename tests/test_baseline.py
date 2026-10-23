"""
Unit tests for Phase 3: Naive Persistence Baseline
"""

import numpy as np
import pytest
from src.baseline import NaivePersistenceBaseline


def test_persistence_prediction_logic():
    # Shape: [2 samples, 3 timesteps, 2 features]
    # Sample 0: feature 0 values: [1.0, 2.0, 3.5] -> latest is 3.5
    # Sample 1: feature 0 values: [4.0, 4.5, 5.0] -> latest is 5.0
    X = np.array([
        [[1.0, 10.0], [2.0, 20.0], [3.5, 30.0]],
        [[4.0, 40.0], [4.5, 50.0], [5.0, 60.0]],
    ])

    baseline = NaivePersistenceBaseline(target_idx=0)
    preds = baseline.predict(X)

    assert preds.shape == (2,)
    assert preds[0] == 3.5
    assert preds[1] == 5.0


def test_persistence_evaluation():
    X = np.array([
        [[1.0], [2.0], [3.0]],
        [[4.0], [5.0], [6.0]],
    ])
    y_true = np.array([3.5, 5.5]) # actual future values

    baseline = NaivePersistenceBaseline(target_idx=0)
    metrics, y_pred = baseline.evaluate(X, y_true)

    # Preds are [3.0, 6.0], true are [3.5, 5.5]. Errors are 0.5, 0.5
    assert metrics["mae"] == 0.5
    assert metrics["rmse"] == 0.5
