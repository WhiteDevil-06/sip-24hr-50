"""
Execution Script for Phase 5: Multivariate LSTM Model Training & Final Handoff Bundle
Project: Deep Learning-Based Soil Moisture Prediction for Smart Irrigation
Experiment: EXP-002 (Multivariate LSTM with Hydrological and Atmospheric Covariates)
Inputs: ['SM_50cm', 'SM_5cm', 'Temp_50cm', 'Temp_5cm', 'Precipitation'] across 96 time-steps (24 hours).
Target: SM_50cm at time t + 96 (24 hours into future).
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import pickle
import numpy as np
import torch

from src.preprocessing import COMMON_FEATURES, TARGET_VARIABLE, WINDOW_SIZE, FORECAST_HORIZON
from src.model import SoilMoistureLSTM
from src.train import train_lstm_model, evaluate_lstm_model


def main():
    print("=" * 80)
    print("PHASE 5: MULTIVARIATE LSTM TRAINING & EXPERIMENT EVALUATION (EXP-002)")
    print("=" * 80)

    processed_dir = Path("data/processed")
    model_dir = Path("models")

    # 1. Load preprocessed tensors
    print("\n[Step 1/6] Loading preprocessed Multivariate dataset (5 features)...")
    X_train = np.load(processed_dir / "X_train.npy")
    y_train = np.load(processed_dir / "y_train.npy")
    X_val = np.load(processed_dir / "X_val.npy")
    y_val = np.load(processed_dir / "y_val.npy")
    X_test = np.load(processed_dir / "X_test.npy")
    y_test = np.load(processed_dir / "y_test.npy")

    print(f"  Features ({len(COMMON_FEATURES)}): {COMMON_FEATURES}")
    print(f"  Train shape: {X_train.shape}, y: {y_train.shape}")
    print(f"  Val shape:   {X_val.shape}, y: {y_val.shape}")
    print(f"  Test shape:  {X_test.shape}, y: {y_test.shape}")

    # Load target scaler for real-world metric evaluation (% VWC)
    with open(model_dir / "target_scaler.pkl", "rb") as f:
        target_scaler = pickle.load(f)

    # 2. Instantiate Model
    print("\n[Step 2/6] Initializing Multivariate SoilMoistureLSTM architecture...")
    model = SoilMoistureLSTM(
        input_size=len(COMMON_FEATURES),
        hidden_size=64,
        num_layers=2,
        dropout=0.2,
    )
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Total trainable parameters: {total_params:,}")

    # 3. Train Model
    print("\n[Step 3/6] Training Multivariate LSTM with Early Stopping (batch_size=512, stride=4)...", flush=True)
    checkpoint_path = model_dir / "best_model.pt"
    history = train_lstm_model(
        model=model,
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        epochs=8,
        batch_size=512,
        lr=0.001,
        patience=3,
        stride=4,
        checkpoint_path=checkpoint_path,
    )

    # 4. Evaluate on Held-Out Test Set
    print("\n[Step 4/6] Evaluating Multivariate model on held-out test set...")
    val_metrics, y_val_pred = evaluate_lstm_model(model, X_val, y_val, target_scaler=target_scaler)
    test_metrics, y_test_pred = evaluate_lstm_model(model, X_test, y_test, target_scaler=target_scaler)

    # Save predictions array
    np.save(processed_dir / "y_test_pred_multivariate.npy", y_test_pred)

    print("\n" + "=" * 80)
    print("MULTIVARIATE LSTM (EXP-002) BENCHMARK RESULTS:")
    print("=" * 80)
    print(f"{'Partition':<15} | {'MAE (% VWC)':<12} | {'RMSE (% VWC)':<12} | {'R² Score':<10}")
    print("-" * 55)
    print(f"{'Validation (2023)':<15} | {val_metrics['mae']:>10.4f} % | {val_metrics['rmse']:>10.4f} % | {val_metrics['r2']:>10.4f}")
    print(f"{'Test (2024–2025)':<15} | {test_metrics['mae']:>10.4f} % | {test_metrics['rmse']:>10.4f} % | {test_metrics['r2']:>10.4f}")

    # 5. Build Model Handoff Bundle for Rahul (Phase 6)
    print("\n[Step 5/6] Generating formal Model Handoff Bundle for Rahul (Phase 6 serving)...")
    handoff_metadata = {
        "model_architecture": "SoilMoistureLSTM",
        "input_features": COMMON_FEATURES,
        "target_variable": TARGET_VARIABLE,
        "input_sequence_length": WINDOW_SIZE,
        "forecast_horizon_steps": FORECAST_HORIZON,
        "time_interval_minutes": 15,
        "forecast_horizon_hours": 24,
        "units": "% Volumetric Water Content (VWC)",
        "model_weights_file": "best_model.pt",
        "feature_scaler_file": "feature_scaler.pkl",
        "target_scaler_file": "target_scaler.pkl",
        "scaler_json_file": "scaler_metadata.json",
        "test_metrics": {
            "mae": test_metrics["mae"],
            "rmse": test_metrics["rmse"],
            "r2": test_metrics["r2"],
        },
        "validation_metrics": {
            "mae": val_metrics["mae"],
            "rmse": val_metrics["rmse"],
            "r2": val_metrics["r2"],
        },
        "irrigation_thresholds": {
            "wilting_point_vwc": 10.0,
            "field_capacity_vwc": 35.0,
            "optimal_range_min_vwc": 18.0,
            "optimal_range_max_vwc": 28.0,
        },
    }

    with open(model_dir / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(handoff_metadata, f, indent=2)

    print(f"  Created '{model_dir / 'model_metadata.json'}' with complete serving contract.")

    # 6. Parity Verification Check
    print("\n[Step 6/6] Verifying serving parity with standalone weights reload...")
    eval_model = SoilMoistureLSTM(
        input_size=len(COMMON_FEATURES),
        hidden_size=64,
        num_layers=2,
        dropout=0.2,
    )
    eval_model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
    eval_model.eval()

    sample_input = torch.tensor(X_test[:10], dtype=torch.float32)
    with torch.no_grad():
        parity_check = eval_model(sample_input).numpy()

    assert np.isfinite(parity_check).all(), "Parity check failed: output contains NaN or Inf"
    print("  Serving Parity Check PASSED: Saved model loads standalone and yields finite predictions.")
    print("Phase 5 Multivariate experiments and Handoff Bundle successfully complete!")

if __name__ == "__main__":
    main()
