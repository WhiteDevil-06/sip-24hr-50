"""
Pytest configuration for the SoilCast test suite.
Sets up sys.path so both src/ and backend/app/ are importable from tests/.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))
