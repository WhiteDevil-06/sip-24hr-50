# Workflow: Implementation & Small Scoped Changes

This workflow governs how code modifications are planned, scoped, and executed to preserve architectural integrity and avoid premature feature creep.

## Step 1: Scope & Acceptance Criteria
- Formulate a precise description of the immediate task.
- Establish measurable acceptance criteria.
- Explicitly list work that is deferred or outside the current scope.

## Step 2: Educational Explanation (Mandatory for Project Lead AI Tasks)
- When implementing AI/ML code with the Project Lead:
  - Explain the underlying mathematics and architecture.
  - Explain the shape of tensors and the meaning of features.
  - Guide the Project Lead through writing and inspecting the code in small increments.

## Step 3: Minimal Diff Implementation
- Edit only target files required for the task.
- Preserve existing docstrings, comments, and unrelated code.
- Avoid large refactorings or speculative architecture.

## Step 4: Trigger Validation Workflow
- Immediately invoke `workflows/code-change-validation.md`.
