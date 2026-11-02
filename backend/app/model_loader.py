"""
Phase 6 — Backend & Model Serving
Model loader: loads SoilMoistureLSTM weights + scalers once at startup.
"""

import json
import pickle
import sys
from pathlib import Path
from typing import Optional

import torch

# Ensure src/ is importable regardless of working directory
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.model import SoilMoistureLSTM  # noqa: E402

# ---------------------------------------------------------------------------
# Global state (populated once at startup)
# ---------------------------------------------------------------------------
_model: Optional[SoilMoistureLSTM] = None
_scaler_meta: Optional[dict] = None
_model_meta: Optional[dict] = None
_load_error: Optional[str] = None


def load_artifacts() -> None:
    """Load model weights and scaler metadata from models/.  Called once."""
    global _model, _scaler_meta, _model_meta, _load_error
    models_dir = ROOT / "models"

    try:
        # --- scaler metadata (JSON, no torch needed) ---
        with open(models_dir / "scaler_metadata.json") as f:
            _scaler_meta = json.load(f)

        # --- model metadata ---
        with open(models_dir / "model_metadata.json") as f:
            _model_meta = json.load(f)

        # --- best model weights (multivariate champion: 5 features) ---
        # The best_model.pt was saved as a full state_dict for the
        # multivariate champion (input_size=5, hidden=64, layers=2, dropout=0.2)
        checkpoint = torch.load(
            models_dir / "best_model.pt",
            map_location="cpu",
            weights_only=False,
        )

        # Detect if checkpoint is a raw state_dict or wrapped dict
        if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]
        elif isinstance(checkpoint, dict) and any(
            k.startswith("lstm.") for k in checkpoint
        ):
            state_dict = checkpoint  # raw state_dict
        else:
            state_dict = checkpoint  # fallback

        n_features = len(_scaler_meta["feature_cols"])
        m = SoilMoistureLSTM(
            input_size=n_features,
            hidden_size=64,
            num_layers=2,
            dropout=0.2,
        )
        m.load_state_dict(state_dict)
        m.eval()
        _model = m

    except Exception as exc:  # pragma: no cover
        _load_error = str(exc)
        _model = None


def get_model() -> SoilMoistureLSTM:
    if _model is None:
        raise RuntimeError(_load_error or "Model not loaded")
    return _model


def get_scaler_meta() -> dict:
    if _scaler_meta is None:
        raise RuntimeError("Scaler metadata not loaded")
    return _scaler_meta


def get_model_meta() -> dict:
    if _model_meta is None:
        raise RuntimeError("Model metadata not loaded")
    return _model_meta


def is_loaded() -> bool:
    return _model is not None


def load_error() -> Optional[str]:
    return _load_error
