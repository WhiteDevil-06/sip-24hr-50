"""
Execution Script for Phase 2: Preprocessing Pipeline
Runs full data ingestion, chronological partitioning, zero-leakage scaler fitting,
sliding window generation, and disk serialization.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
from src.preprocessing import (
    COMMON_FEATURES,
    TARGET_VARIABLE,
    WINDOW_SIZE,
    FORECAST_HORIZON,
    load_raw_dataset,
    split_chronological,
    PreprocessingPipeline,
)

def main():
    print("=" * 80)
    print("PHASE 2: PREPROCESSING PIPELINE & SLIDING WINDOW GENERATION")
    print("=" * 80)

    # 1. Load standardized raw data
    print("\n[Step 1/5] Loading raw datasets (2016–2025, excluding 2021 transition)...")
    full_df = load_raw_dataset(raw_dir=Path("data/raw"))
    print(f"Loaded {len(full_df):,} total records across all operational years.")
    print(f"Timestamp range: {full_df['timestamp'].min()} to {full_df['timestamp'].max()}")

    # 2. Chronological partition
    print("\n[Step 2/5] Partitioning data chronologically...")
    train_df, val_df, test_df = split_chronological(full_df)
    print(f"  Training set:   {len(train_df):>7,} rows ({train_df['timestamp'].min().date()} to {train_df['timestamp'].max().date()})")
    print(f"  Validation set: {len(val_df):>7,} rows ({val_df['timestamp'].min().date()} to {val_df['timestamp'].max().date()})")
    print(f"  Test set:       {len(test_df):>7,} rows ({test_df['timestamp'].min().date()} to {test_df['timestamp'].max().date()})")

    # 3. Fit scalers strictly on training data
    print("\n[Step 3/5] Fitting MinMaxScaler strictly on training set (zero lookahead leakage)...")
    pipeline = PreprocessingPipeline(
        feature_cols=COMMON_FEATURES,
        target_col=TARGET_VARIABLE,
        window_size=WINDOW_SIZE,
        horizon=FORECAST_HORIZON,
    )
    pipeline.fit_scalers(train_df)

    # Save scaler artifacts
    model_dir = Path("models")
    pipeline.save_artifacts(model_dir)
    print(f"  Saved feature_scaler.pkl, target_scaler.pkl, and scaler_metadata.json to '{model_dir}'.")

    # 4. Generate 3D sliding window tensors
    print("\n[Step 4/5] Generating sliding window tensors (T = 96 steps -> horizon = 96 steps)...")
    print("  Creating training sequences...")
    X_train, y_train, meta_train = pipeline.create_sliding_windows(train_df, apply_scaling=True)
    print(f"    Train X shape: {X_train.shape}, y shape: {y_train.shape}")

    print("  Creating validation sequences...")
    X_val, y_val, meta_val = pipeline.create_sliding_windows(val_df, apply_scaling=True)
    print(f"    Val X shape:   {X_val.shape}, y shape: {y_val.shape}")

    print("  Creating held-out test sequences...")
    X_test, y_test, meta_test = pipeline.create_sliding_windows(test_df, apply_scaling=True)
    print(f"    Test X shape:  {X_test.shape}, y shape: {y_test.shape}")

    # 5. Persist processed tensors to data/processed/
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n[Step 5/5] Saving preprocessed arrays to '{processed_dir}'...")

    np.save(processed_dir / "X_train.npy", X_train)
    np.save(processed_dir / "y_train.npy", y_train)
    np.save(processed_dir / "X_val.npy", X_val)
    np.save(processed_dir / "y_val.npy", y_val)
    np.save(processed_dir / "X_test.npy", X_test)
    np.save(processed_dir / "y_test.npy", y_test)
    meta_test.to_csv(processed_dir / "meta_test.csv", index=False)

    print("\n" + "=" * 80)
    print("PREPROCESSING PIPELINE VALIDATION SUMMARY:")
    print("=" * 80)
    print(f"Features utilized ({len(COMMON_FEATURES)}): {COMMON_FEATURES}")
    print(f"Input sequence window:  {WINDOW_SIZE} time steps (24.0 hours)")
    print(f"Target forecast offset: {FORECAST_HORIZON} time steps (24.0 hours ahead)")
    print(f"Tensors serialized:     X_train ({X_train.shape}), X_val ({X_val.shape}), X_test ({X_test.shape})")
    print("Phase 2 processing successfully verified and complete!")

if __name__ == "__main__":
    main()
