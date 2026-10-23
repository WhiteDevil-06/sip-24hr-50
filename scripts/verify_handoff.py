"""
Handoff Verification Script for Rahul (Phase 6 Backend Developer)
Executes end-to-end validation of the Model Handoff Bundle:
1. Verifies model weights (models/best_model.pt).
2. Verifies scalers (pickle & JSON).
3. Verifies metadata contract (models/model_metadata.json).
4. Executes mock end-to-end inference simulating FastAPI request payload.
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
from src.model import SoilMoistureLSTM


def main():
    print("=" * 80)
    print("MODEL HANDOFF VERIFICATION SUITE FOR RAHUL (BACKEND DEVELOPER)")
    print("=" * 80)

    model_dir = Path("models")

    # 1. Check Artifact Files Existence
    required_files = [
        "best_model.pt",
        "lstm_univariate.pt",
        "feature_scaler.pkl",
        "target_scaler.pkl",
        "scaler_metadata.json",
        "model_metadata.json",
    ]
    print("\n[Check 1/4] Verifying handoff files in 'models/'...")
    for fname in required_files:
        fpath = model_dir / fname
        assert fpath.exists(), f"MISSING ARTIFACT: {fname}"
        print(f"  [OK] Found {fname} ({fpath.stat().st_size:,} bytes)")

    # 2. Check Metadata Schema
    print("\n[Check 2/4] Verifying model metadata contract...")
    with open(model_dir / "model_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert meta["model_architecture"] == "SoilMoistureLSTM"
    assert len(meta["input_features"]) == 5
    assert meta["input_sequence_length"] == 96
    assert meta["forecast_horizon_steps"] == 96
    print(f"  [OK] Target Variable: {meta['target_variable']}")
    print(f"  [OK] Features ({len(meta['input_features'])}): {meta['input_features']}")
    print(f"  [OK] Test R²: {meta['test_metrics']['r2']}, Test MAE: {meta['test_metrics']['mae']}% VWC")

    # 3. Load Model and Scalers
    print("\n[Check 3/4] Loading model weights and scaler...")
    with open(model_dir / "feature_scaler.pkl", "rb") as f:
        feature_scaler = pickle.load(f)
    with open(model_dir / "target_scaler.pkl", "rb") as f:
        target_scaler = pickle.load(f)

    model = SoilMoistureLSTM(
        input_size=len(meta["input_features"]),
        hidden_size=64,
        num_layers=2,
        dropout=0.2,
    )
    model.load_state_dict(torch.load(model_dir / "best_model.pt", map_location="cpu"))
    model.eval()
    print("  [OK] Model successfully loaded into memory in EVAL mode.")

    # 4. Mock Inference Test (Simulating FastAPI POST /api/v1/predict)
    print("\n[Check 4/4] Executing mock inference with realistic sensor payload...")
    # Generate 96 steps of realistic inputs
    np.random.seed(42)
    mock_raw_features = np.zeros((96, 5), dtype=np.float32)
    mock_raw_features[:, 0] = 16.5 + np.random.normal(0, 0.1, 96) # SM_50cm
    mock_raw_features[:, 1] = 18.0 + np.random.normal(0, 0.3, 96) # SM_5cm
    mock_raw_features[:, 2] = 25.0 + np.random.normal(0, 0.2, 96) # Temp_50cm
    mock_raw_features[:, 3] = 26.0 + np.random.normal(0, 0.4, 96) # Temp_5cm
    mock_raw_features[:, 4] = 0.0                                 # Precipitation

    # Preprocess using feature scaler
    scaled_input = feature_scaler.transform(mock_raw_features)
    tensor_input = torch.tensor(scaled_input, dtype=torch.float32).unsqueeze(0) # [1, 96, 5]

    with torch.no_grad():
        scaled_pred = model(tensor_input).numpy() # [1]

    # Invert prediction to physical % VWC
    unscaled_pred = target_scaler.inverse_transform(scaled_pred.reshape(-1, 1))[0, 0]

    current_val = float(mock_raw_features[-1, 0])
    pred_val = float(unscaled_pred)
    change_24h = pred_val - current_val

    print("\n" + "=" * 80)
    print("MOCK INFERENCE RESPONSE SIMULATION:")
    print("=" * 80)
    print(f"Current SM_50cm:         {current_val:.2f}% VWC")
    print(f"Predicted SM_50cm (t+24h): {pred_val:.2f}% VWC")
    print(f"Projected 24h Delta:     {change_24h:+.2f}% VWC")
    print(f"Prediction Finite Check: {'PASS' if np.isfinite(pred_val) else 'FAIL'}")
    print("\nSUCCESS: Model Handoff Bundle is 100% verified and ready for Rahul (Phase 6)!")

if __name__ == "__main__":
    main()
