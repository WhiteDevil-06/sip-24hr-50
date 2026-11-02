#!/usr/bin/env python3
"""
Convenience launcher for the SoilCast FastAPI backend.

Can be run from anywhere:
  - From project root:   python backend/run.py
  - From backend dir:    cd backend && python run.py
  - Optional arguments:  python backend/run.py --port 8000 --host 127.0.0.1
"""

import argparse
import os
import sys
from pathlib import Path

# 1. Ensure repo root and backend directory are always on sys.path
BACKEND_DIR = Path(__file__).resolve().parent
REPO_ROOT = BACKEND_DIR.parent

for p in (str(REPO_ROOT), str(BACKEND_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import torch
    import fastapi
    import uvicorn
except ImportError as err:
    print("\n" + "=" * 65)
    print("❌ MISSING DEPENDENCIES ERROR:")
    print(f"   {err}")
    print("\n   To fix this, install the required packages:")
    print("   pip install fastapi uvicorn pydantic numpy")
    print("   pip install torch --index-url https://download.pytorch.org/whl/cpu")
    print("=" * 65 + "\n")
    sys.exit(1)

from app.main import app

def main():
    parser = argparse.ArgumentParser(description="SoilCast Backend API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port number (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    print("\n" + "=" * 65)
    print("🌱 SoilCast — Soil Moisture Forecasting Service")
    print("=" * 65)
    print(f"• Server URL:        http://{args.host}:{args.port}")
    print(f"• Swagger API Docs:  http://{args.host}:{args.port}/docs")
    print(f"• Health Check:      http://{args.host}:{args.port}/health")
    print(f"• Forecast API:      http://{args.host}:{args.port}/api/forecast")
    print("=" * 65)
    print("Loading PyTorch model and scalers at startup...\n")

    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )

if __name__ == "__main__":
    main()
