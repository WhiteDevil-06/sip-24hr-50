# Subsystem Rules: Dependency Management

These rules ensure reproducible environments and prevent environment contamination.

## 1. Python Environment Management
- All Python packages must be managed within an isolated virtual environment (`.venv` or `venv`).
- Global `pip install` commands without virtual environments are prohibited.
- Pin or lock direct dependencies in manifest files (`requirements.txt`, `pyproject.toml`, or `Pipfile`).
- Before running scripts, verify that the virtual environment interpreter is active.

## 2. JavaScript / Node Management
- Use `npm` or `pnpm` to manage frontend dependencies.
- Commit `package.json` and `package-lock.json` to guarantee reproducible builds across developer machines.
- Avoid installing unnecessary heavy libraries or dependencies without clear justification.
