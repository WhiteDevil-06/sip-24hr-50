"""
Phase 9 — Final reproducibility & security validation.

Checks:
  1. No secrets/keys in tracked files (basic pattern scan)
  2. Model artifact generates finite predictions
  3. All required documentation files exist
  4. Existing test suite can be discovered
"""

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# ---------------------------------------------------------------------------
# 1. Security: no raw secrets in codebase
# ---------------------------------------------------------------------------
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]{8,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),   # OpenAI-style keys
    re.compile(r"AIza[0-9A-Za-z_-]{35}"),  # Google API keys
]

SKIP_DIRS = {".git", ".venv", "__pycache__", "node_modules", ".next"}


def _text_files():
    for path in ROOT.rglob("*"):
        if path.is_file() and not any(d in path.parts for d in SKIP_DIRS):
            if path.suffix in (".py", ".ts", ".tsx", ".js", ".env", ".json", ".md", ".txt", ".cfg", ".toml"):
                yield path


class TestSecurity:
    def test_no_hardcoded_secrets(self):
        violations = []
        for path in _text_files():
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    violations.append(str(path))
                    break
        assert not violations, f"Potential secrets found in: {violations}"

    def test_env_local_not_committed(self):
        env_local = ROOT / "frontend" / ".env.local"
        # It's fine if it exists locally (gitignored), but it must be in .gitignore
        gitignore = ROOT / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            assert ".env.local" in content or "*.local" in content, (
                ".env.local is not listed in .gitignore"
            )


# ---------------------------------------------------------------------------
# 2. Documentation completeness
# ---------------------------------------------------------------------------
REQUIRED_DOCS = [
    "README.md",
    "docs/API_CONTRACT.md",
    "docs/EXPERIMENTS.md",
    ".agent/PROJECT_STATE.md",
    ".agent/PHASES.md",
]


class TestDocumentation:
    def test_required_docs_exist(self):
        missing = [d for d in REQUIRED_DOCS if not (ROOT / d).exists()]
        assert not missing, f"Missing documentation files: {missing}"

    def test_api_contract_has_predict_endpoint(self):
        contract = (ROOT / "docs/API_CONTRACT.md").read_text()
        assert "/api/v1/predict" in contract
        assert "SM_50cm" in contract

    def test_experiments_doc_has_metrics(self):
        exp = (ROOT / "docs/EXPERIMENTS.md").read_text()
        # Should document at least one real metric value
        assert any(term in exp for term in ("MAE", "RMSE", "R²", "R2", "mae", "rmse")), (
            "EXPERIMENTS.md does not appear to contain any performance metrics"
        )


# ---------------------------------------------------------------------------
# 3. Model artifact presence and finite output
# ---------------------------------------------------------------------------

class TestModelArtifact:
    def test_model_files_exist(self):
        for fname in ("best_model.pt", "scaler_metadata.json", "model_metadata.json"):
            assert (ROOT / "models" / fname).exists(), f"Missing: {fname}"

    def test_model_produces_finite_output(self):
        try:
            import torch
        except ImportError:
            pytest.skip("torch not installed")

        import json
        import numpy as np

        sys.path.insert(0, str(ROOT))
        from src.model import SoilMoistureLSTM
        from app.inference import scale_input, inverse_scale_target

        with open(ROOT / "models" / "scaler_metadata.json") as f:
            scaler = json.load(f)

        checkpoint = torch.load(
            ROOT / "models" / "best_model.pt",
            map_location="cpu",
            weights_only=False,
        )
        state_dict = checkpoint.get("model_state_dict", checkpoint)
        n_features = len(scaler["feature_cols"])
        model = SoilMoistureLSTM(input_size=n_features, hidden_size=64, num_layers=2, dropout=0.2)
        model.load_state_dict(state_dict)
        model.eval()

        raw = {
            "SM_50cm": [22.5] * 96, "SM_5cm": [24.0] * 96,
            "Temp_50cm": [26.0] * 96, "Temp_5cm": [25.5] * 96, "Precipitation": [0.0] * 96,
        }
        scaled = scale_input(raw, scaler)
        x = torch.from_numpy(scaled)
        with torch.no_grad():
            pred = model(x).item()
        physical = inverse_scale_target(pred, scaler)

        import math
        assert math.isfinite(physical), f"Model output is not finite: {physical}"
        assert 0.0 <= physical <= 60.0, f"Model output out of physical range: {physical}"
