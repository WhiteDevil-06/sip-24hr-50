"""
Unit Tests for Phase 2: Preprocessing Pipeline & Sliding Window Generator
Verifies:
1. Zero lookahead leakage in chronological split.
2. Scaler fitted strictly on training data.
3. 3D tensor output shapes [batch, 96, num_features].
4. Strict temporal alignment: Target timestamp == Input end timestamp + 24 hours.
5. Scaler serialization roundtrip (pickle & JSON).
"""

import sys
from pathlib import Path
import tempfile
import pytest
import numpy as np
import pandas as pd

from src.preprocessing import (
    COMMON_FEATURES,
    TARGET_VARIABLE,
    WINDOW_SIZE,
    FORECAST_HORIZON,
    split_chronological,
    PreprocessingPipeline,
)


@pytest.fixture
def synthetic_timeseries():
    """
    Creates a continuous synthetic 15-minute time-series covering 2022 to 2024.
    """
    dates = pd.date_range("2022-01-01", "2024-03-01", freq="15min")
    n = len(dates)
    np.random.seed(42)

    df = pd.DataFrame({
        "timestamp": dates,
        "SM_50cm": np.clip(15.0 + 5.0 * np.sin(np.linspace(0, 50, n)) + np.random.normal(0, 0.2, n), 0, 50),
        "SM_5cm": np.clip(18.0 + 8.0 * np.sin(np.linspace(0, 100, n)) + np.random.normal(0, 0.5, n), 0, 50),
        "Temp_50cm": 25.0 + 2.0 * np.cos(np.linspace(0, 20, n)),
        "Temp_5cm": 25.0 + 4.0 * np.cos(np.linspace(0, 40, n)),
        "Precipitation": np.random.choice([0.0, 0.0, 0.0, 1.2, 3.5], size=n, p=[0.90, 0.05, 0.03, 0.015, 0.005]),
    })
    return df


def test_chronological_split_no_leakage(synthetic_timeseries):
    train_df, val_df, test_df = split_chronological(synthetic_timeseries)

    # 1. Assert non-empty splits
    assert len(train_df) > 0, "Train split must not be empty"
    assert len(val_df) > 0, "Validation split must not be empty"
    assert len(test_df) > 0, "Test split must not be empty"

    # 2. Strict chronological ordering (no overlap / zero leakage)
    assert train_df["timestamp"].max() < val_df["timestamp"].min(), "Train overlaps with Val!"
    assert val_df["timestamp"].max() < test_df["timestamp"].min(), "Val overlaps with Test!"

    # 3. Partition boundaries
    assert train_df["timestamp"].max() < pd.to_datetime("2023-01-01")
    assert val_df["timestamp"].min() >= pd.to_datetime("2023-01-01")
    assert val_df["timestamp"].max() < pd.to_datetime("2024-01-01")
    assert test_df["timestamp"].min() >= pd.to_datetime("2024-01-01")


def test_scaler_isolation(synthetic_timeseries):
    train_df, val_df, test_df = split_chronological(synthetic_timeseries)

    pipeline = PreprocessingPipeline(feature_cols=COMMON_FEATURES)
    pipeline.fit_scalers(train_df)

    assert pipeline.fitted is True

    # Assert that scaler minimum and maximum are derived ONLY from train_df
    for i, col in enumerate(COMMON_FEATURES):
        expected_min = train_df[col].min()
        expected_max = train_df[col].max()
        np.testing.assert_almost_equal(pipeline.feature_scaler.data_min_[i], expected_min, decimal=4)
        np.testing.assert_almost_equal(pipeline.feature_scaler.data_max_[i], expected_max, decimal=4)


def test_sliding_window_shapes_and_temporal_alignment(synthetic_timeseries):
    train_df, _, _ = split_chronological(synthetic_timeseries)

    pipeline = PreprocessingPipeline(
        feature_cols=COMMON_FEATURES,
        window_size=96,
        horizon=96,
    )
    pipeline.fit_scalers(train_df)

    # Take a small sub-slice of train_df (e.g. 1000 rows)
    sub_df = train_df.iloc[:1000].copy()
    X, y, meta = pipeline.create_sliding_windows(sub_df, apply_scaling=True)

    # Assert tensor dimensions: [N, 96, 5]
    assert X.ndim == 3
    assert X.shape[1] == 96
    assert X.shape[2] == len(COMMON_FEATURES)
    assert y.ndim == 1
    assert len(X) == len(y) == len(meta)

    # Values must be normalized within [0, 1] range (or very close due to slight float noise)
    assert np.all(X >= -0.01) and np.all(X <= 1.01)

    # Strict physical temporal alignment test for every window:
    # Target time MUST BE exactly input_end + 24 hours
    for idx, row in meta.iterrows():
        input_end = row["input_end"]
        target_time = row["target_time"]
        diff = target_time - input_end
        assert diff == pd.Timedelta(hours=24), f"Window {idx} temporal alignment failed: {diff}"


def test_scaler_serialization_roundtrip(synthetic_timeseries):
    train_df, _, _ = split_chronological(synthetic_timeseries)

    pipeline = PreprocessingPipeline(feature_cols=COMMON_FEATURES)
    pipeline.fit_scalers(train_df)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        pipeline.save_artifacts(tmp_path)

        # Assert artifacts exist
        assert (tmp_path / "feature_scaler.pkl").exists()
        assert (tmp_path / "target_scaler.pkl").exists()
        assert (tmp_path / "scaler_metadata.json").exists()

        # Reload
        new_pipeline = PreprocessingPipeline()
        new_pipeline.load_artifacts(tmp_path)

        # Verify numerical equivalence
        sample_input = train_df[COMMON_FEATURES].iloc[:10].values
        out1 = pipeline.feature_scaler.transform(sample_input)
        out2 = new_pipeline.feature_scaler.transform(sample_input)
        np.testing.assert_array_almost_equal(out1, out2)
