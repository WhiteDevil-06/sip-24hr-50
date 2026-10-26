#!/usr/bin/env python3
"""
Convenience launcher for the SoilCast FastAPI backend.
Run from project root:  python backend/run.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        app_dir="backend",
    )
