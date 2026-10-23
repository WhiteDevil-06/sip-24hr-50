"""
Execution Script for Phase 4: Univariate LSTM Model Training & Evaluation
Project: Deep Learning-Based Soil Moisture Prediction for Smart Irrigation
Experiment: EXP-001 (Univariate LSTM)
Input: Historical SM_50cm across 96 time-steps (24 hours).
Target: SM_50cm at time t + 96 (24 hours into future).
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pickle
import numpy as np
import torch

from src.model import SoilMoistureLSTM
from src.train import train_lstm_model, evaluate_lstm_model


def main():
    print("=" * 80)
    print("PHASE 4: UNIVARIATE LSTM TRAINING & BENCHMARK EVALUATION (EXP-001)")
    print("=" * 80)

    processed_dir = Path("data/processed")
    model_dir = Path("models")

    # 1. Load preprocessed tensors
    print("\n[Step 1/5] Loading preprocessed data and extracting Univariate slice (Feature 0: SM_50cm)...")
    X_train_full = np.load(processed_dir / "X_train.npy")
    y_train = np.load(processed_dir / "y_train.npy")
    X_val_full = np.load(processed_dir / "X_val.npy")
    y_val = np.load(processed_dir / "y_val.npy")
    X_test_full = np.load(processed_dir / "X_test.npy")
    y_test = np.load(processed_dir / "y_test.npy")

    # Univariate slice: feature 0 only (SM_50cm)
    X_train_uni = X_train_full[:, :, :1]
    X_val_uni = X_val_full[:, :, :1]
    X_test_uni = X_test_full[:, :, :1]

    print(f"  Univariate Train shape: {X_train_uni.shape}, y: {y_train.shape}")
    print(f"  Univariate Val shape:   {X_val_uni.shape}, y: {y_val.shape}")
    print(f"  Univariate Test shape:  {X_test_uni.shape}, y: {y_test.shape}")

    # Load target scaler for real-world metric evaluation (% VWC)
    with open(model_dir / "target_scaler.pkl", "rb") as f:
        target_scaler = pickle.load(f)

    # 2. Instantiate Model
    print("\n[Step 2/5] Initializing SoilMoistureLSTM architecture...")
    model = SoilMoistureLSTM(
        input_size=1,
        hidden_size=64,
        num_layers=2,
        dropout=0.2,
    )
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Total trainable parameters: {total_params:,}")

    # 3. Train Model
    print("\n[Step 3/5] Training model with Early Stopping (batch_size=512, stride=4)...", flush=True)
    checkpoint_path = model_dir / "lstm_univariate.pt"
    history = train_lstm_model(
        model=model,
        X_train=X_train_uni,
        y_train=y_train,
        X_val=X_val_uni,
        y_val=y_val,
        epochs=8,
        batch_size=512,
        lr=0.001,
        patience=3,
        stride=4,
        checkpoint_path=checkpoint_path,
    )

    # 4. Standalone Inference Reload Verification
    print("\n[Step 4/5] Verifying standalone model artifact reloadability...")
    reload_model = SoilMoistureLSTM(input_size=1, hidden_size=64, num_layers=2, dropout=0.2)
    reload_model.load_state_dict(torch.load(checkpoint_path, map_location="cpu"))
    reload_model.eval()

    sample_input = torch.tensor(X_test_uni[:5], dtype=torch.float32)
    with torch.no_grad():
        orig_out = model(sample_input).numpy()
        reloaded_out = reload_model(sample_input).numpy()
    np.testing.assert_allclose(orig_out, reloaded_out, rtol=1e-5, atol=1e-5)
    print("  Reload check PASSED: Loaded artifact yields numerically identical predictions (rtol < 1e-5)!")

    # 5. Evaluate on Held-Out Test Set
    print("\n[Step 5/5] Evaluating on held-out test set against Persistence baseline...")
    val_metrics, y_val_pred = evaluate_lstm_model(reload_model, X_val_uni, y_val, target_scaler=target_scaler)
    test_metrics, y_test_pred = evaluate_lstm_model(reload_model, X_test_uni, y_test, target_scaler=target_scaler)

    print("\n" + "=" * 80)
    print("UNIVARIATE LSTM (EXP-001) EVALUATION RESULTS:")
    print("=" * 80)
    print(f"{'Partition':<15} | {'MAE (% VWC)':<12} | {'RMSE (% VWC)':<12} | {'R² Score':<10}")
    print("-" * 55)
    print(f"{'Validation (2023)':<15} | {val_metrics['mae']:>10.4f} % | {val_metrics['rmse']:>10.4f} % | {val_metrics['r2']:>10.4f}")
    print(f"{'Test (2024–2025)':<15} | {test_metrics['mae']:>10.4f} % | {test_metrics['rmse']:>10.4f} % | {test_metrics['r2']:>10.4f}")

    print("\nBenchmark Comparison vs. Naïve Persistence (EXP-000):")
    print("  Persistence Test: MAE = 0.6949 %, RMSE = 1.4206 %, R² = 0.8303")
    print(f"  Univariate LSTM:  MAE = {test_metrics['mae']:.4f} %, RMSE = {test_metrics['rmse']:.4f} %, R² = {test_metrics['r2']:.4f}")

    # Save predictions array for analysis
    np.save(processed_dir / "y_test_pred_univariate.npy", y_test_pred)
    print(f"\nSaved univariate predictions to '{processed_dir / 'y_test_pred_univariate.npy'}'.")
    print("Phase 4 Univariate LSTM training and verification successfully complete!")

if __name__ == "__main__":
    main()
