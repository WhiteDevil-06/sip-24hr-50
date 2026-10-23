# Subsystem Rules: Dependency Management

These rules ensure reproducible environments and prevent environment contamination.

## 1. Python Environment Management
- All Python packages must be managed within the isolated virtual environment (`.venv`).
- Global `pip install` commands without virtual environments are strictly prohibited.
- **Package Manager:** Per ADR-0003, use `uv` (`.venv\Scripts\uv.exe pip install ...`) as the primary fast package manager for all Python package additions and lock management.
- Pin or lock direct dependencies in manifest files (`requirements.txt`, `pyproject.toml`).
- Before running scripts, verify that the `.venv` interpreter (`.venv\Scripts\python.exe`) is active.

## 2. JavaScript / Node Management
- Use `npm` or `pnpm` to manage frontend dependencies.
- Commit `package.json` and `package-lock.json` to guarantee reproducible builds across developer machines.
- Avoid installing unnecessary heavy libraries or dependencies without clear justification.
