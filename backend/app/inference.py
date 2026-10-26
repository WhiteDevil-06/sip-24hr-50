"""
Phase 6 — Preprocessing helper for inference.
Applies the exact same MinMax scaling used during training (from scaler_metadata.json).
No sklearn dependency at inference time — pure numpy.
"""

import math
from typing import List

import numpy as np

FEATURE_COLS = ["SM_50cm", "SM_5cm", "Temp_50cm", "Temp_5cm", "Precipitation"]


def scale_input(
    raw_features: dict[str, List[float]],
    scaler_meta: dict,
) -> np.ndarray:
    """
    Scale raw feature arrays using stored MinMax parameters.

    Returns:
        np.ndarray of shape (1, 96, 5) — ready for model forward pass.
    """
    n = len(raw_features["SM_50cm"])  # should be 96
    matrix = np.empty((n, len(FEATURE_COLS)), dtype=np.float32)

    for col_idx, col in enumerate(FEATURE_COLS):
        feat_idx = scaler_meta["feature_cols"].index(col)
        scale = scaler_meta["features_scale"][feat_idx]
        min_off = scaler_meta["features_min_offset"][feat_idx]
        arr = np.array(raw_features[col], dtype=np.float32)
        # MinMaxScaler: X_scaled = X * scale + min_offset
        matrix[:, col_idx] = arr * scale + min_off

    return matrix[np.newaxis, :, :]  # (1, 96, 5)


def inverse_scale_target(scaled_value: float, scaler_meta: dict) -> float:
    """Invert MinMax scaling on the SM_50cm target prediction."""
    t_scale = scaler_meta["target_scale"]
    t_min_off = scaler_meta["target_min_offset"]
    # X_original = (X_scaled - min_offset) / scale
    return float((scaled_value - t_min_off) / t_scale)


def build_irrigation_advisory(
    current_sm: float,
    predicted_sm: float,
    meta: dict,
) -> dict:
    """Generate irrigation recommendation based on thresholds from model_metadata."""
    thresholds = meta.get("irrigation_thresholds", {})
    wilting = thresholds.get("wilting_point_vwc", 10.0)
    field_cap = thresholds.get("field_capacity_vwc", 35.0)
    opt_min = thresholds.get("optimal_range_min_vwc", 18.0)
    opt_max = thresholds.get("optimal_range_max_vwc", 28.0)

    if predicted_sm < wilting:
        recommendation = "CRITICAL_DEFICIT"
        action_required = True
        urgency = "immediate"
        explanation = (
            f"Soil moisture is projected to drop to {predicted_sm:.2f}% VWC — "
            f"below the wilting point ({wilting}%). Immediate irrigation required."
        )
    elif predicted_sm < opt_min:
        recommendation = "DEFICIT_ALERT"
        action_required = True
        urgency = "high"
        explanation = (
            f"Soil moisture is projected at {predicted_sm:.2f}% VWC — "
            f"below the optimal range ({opt_min}–{opt_max}%). Consider irrigation."
        )
    elif predicted_sm > field_cap:
        recommendation = "EXCESS_MOISTURE"
        action_required = False
        urgency = "none"
        explanation = (
            f"Soil moisture is projected at {predicted_sm:.2f}% VWC — "
            f"above field capacity ({field_cap}%). No irrigation needed; check drainage."
        )
    else:
        recommendation = "OPTIMAL_MOISTURE"
        action_required = False
        urgency = "none"
        explanation = (
            f"Soil moisture at 50 cm root zone is projected to remain stable at "
            f"{predicted_sm:.2f}% VWC over the next 24 hours. No immediate irrigation required."
        )

    return {
        "recommendation": recommendation,
        "action_required": action_required,
        "urgency": urgency,
        "current_value": round(current_sm, 4),
        "predicted_value": round(predicted_sm, 4),
        "optimal_range_min": opt_min,
        "optimal_range_max": opt_max,
        "wilting_point": wilting,
        "field_capacity": field_cap,
        "explanation": explanation,
    }
