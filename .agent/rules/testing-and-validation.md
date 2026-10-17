# Subsystem Rules: Testing & Mandatory Validation

Validation is mandatory for every meaningful code change. Untested code must never be merged or claimed as complete.

## 1. Test Categories
- **Unit Tests:** Verify individual functions (preprocessing steps, metric formulas, Pydantic schemas, React components).
- **Inference Parity Tests:** Verify that backend serving produces predictions identical to the standalone trained model within $< 10^{-5}$ tolerance.
- **Static Checks & Linting:**
  - Python: Flake8 / Ruff or Pytest.
  - TypeScript: `tsc --noEmit` and ESLint.
- **Build Checks:** Next.js production build (`npm run build`) before phase sign-off.

## 2. Test Execution Rules
- Run tests in real terminals via `run_command`.
- Report exact commands executed and stdout/stderr outcomes.
- Never weaken assertions or delete tests merely to make them pass.
- Mark tests as `NOT RUN` or `BLOCKED` if they were not executed.
