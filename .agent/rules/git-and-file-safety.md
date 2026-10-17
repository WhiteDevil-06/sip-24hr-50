# Subsystem Rules: Git & File Safety

These rules govern file modification safety, data preservation, and version control discipline.

## 1. File Inspection & Cleanliness
- Always inspect `git status` before making edits to ensure no uncommitted work is unintentionally modified or discarded.
- Avoid hardcoded absolute paths in project code; use repository-relative paths (`pathlib.Path` or project root resolution).

## 2. Raw Data Protection
- Raw dataset files downloaded into `data/raw/` must NEVER be modified or overwritten.
- All transformations, imputations, and feature engineering scripts must write to separate processed directories (`data/processed/`).

## 3. Safe Git Operations
- Never execute destructive git commands (`git reset --hard`, `git clean -fd`, `git checkout .`, `git push --force`) without explicit human instruction.
- Never rewrite git history or delete branches without authorization.
- Never commit large binaries, virtual environments (`venv/`), Node modules (`node_modules/`), or raw datasets to the repository.
