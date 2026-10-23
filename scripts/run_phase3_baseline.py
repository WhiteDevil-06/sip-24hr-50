"""
Execution Script for Phase 3: Naïve Persistence Baseline Evaluation
Evaluates Naïve Persistence (y_hat_{t+96} = y_t) across Validation and Held-Out Test sets.
Calculates official baseline benchmark metrics: MAE, RMSE, R^2.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pickle
import numpy as np
from src.baseline import NaivePersistenceBaseline


def main():
    print("=" * 80)
    print("PHASE 3: NAÏVE PERSISTENCE BASELINE EVALUATION")
    print("=" * 80)

    processed_dir = Path("data/processed")
    model_dir = Path("models")

    # 1. Load preprocessed tensors
    print("\n[Step 1/3] Loading processed validation and test tensors...")
    X_val = np.load(processed_dir / "X_val.npy")
    y_val = np.load(processed_dir / "y_val.npy")
    X_test = np.load(processed_dir / "X_test.npy")
    y_test = np.load(processed_dir / "y_test.npy")

    print(f"  Validation samples: {len(X_val):,}")
    print(f"  Test samples:       {len(X_test):,}")

    # 2. Load target scaler for unscaled physical evaluation (% VWC)
    target_scaler_path = model_dir / "target_scaler.pkl"
    with open(target_scaler_path, "rb") as f:
        target_scaler = pickle.load(f)

    baseline = NaivePersistenceBaseline(target_idx=0)

    # 3. Evaluate on Validation and Test sets
    print("\n[Step 2/3] Evaluating Naïve Persistence (y_hat_{t+96} = y_t)...")
    val_metrics, y_val_pred = baseline.evaluate(X_val, y_val, target_scaler=target_scaler)
    test_metrics, y_test_pred = baseline.evaluate(X_test, y_test, target_scaler=target_scaler)

    print("\n" + "=" * 80)
    print("EMPIRICAL BASELINE METRICS (PHYSICAL UNITS: % VWC)")
    print("=" * 80)
    print(f"{'Partition':<15} | {'Test MAE':<10} | {'Test RMSE':<10} | {'Test R²':<10}")
    print("-" * 55)
    print(f"{'Validation (2023)':<15} | {val_metrics['mae']:>8.4f} % | {val_metrics['rmse']:>8.4f} % | {val_metrics['r2']:>8.4f}")
    print(f"{'Test (2024–2025)':<15} | {test_metrics['mae']:>8.4f} % | {test_metrics['rmse']:>8.4f} % | {test_metrics['r2']:>8.4f}")

    print("\n[Step 3/3] Baseline Summary & Significance:")
    print(f"1. Soil moisture at 50 cm depth displays remarkable persistence (Test R² = {test_metrics['r2']:.4f}).")
    print(f"2. Average 24-hour error of simple persistence is MAE = {test_metrics['mae']:.2f}% VWC.")
    print("3. Deep learning models in Phase 4 & 5 must achieve MAE < {:.4f} and R² > {:.4f} to demonstrate value.".format(test_metrics['mae'], test_metrics['r2']))
    print("Phase 3 baseline evaluation successfully complete!")

if __name__ == "__main__":
    main()
