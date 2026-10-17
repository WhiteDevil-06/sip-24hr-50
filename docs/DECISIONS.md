# Architecture Decision Records (ADRs)

This document tracks significant design choices, architectural decisions, and governance policies adopted throughout the project lifecycle.

---

## ADR-0001: Phase 0 Project Initialization & Governance System
- **Date:** 2026-10-17
- **Status:** APPROVED
- **Context:**
  The project requires a multi-role team (Project Lead, Ram Charan for Frontend, Rahul for Backend) operating in an academic research context with rigorous engineering standards. A shared repository must enforce role boundaries, phase gates, and mandatory validation to ensure reproducibility and prevent unverified bulk code generation.
- **Decision:**
  Establish a version-controlled `.agent/` directory with:
  1. Immutable Global Rules (A through M).
  2. 10 gated phases with explicit acceptance criteria.
  3. Strict role definition files for Project Lead, Website Developer, and Backend Developer.
  4. 11 specialist review checklists.
  5. Discovery entry points (`AGENTS.md` and `GEMINI.md`).
- **Consequences:**
  - Standardizes development practices across all team members.
  - Enforces explicit procedural reviews before phase transitions.
  - Prevents premature code generation for downstream phases.

---

## ADR-0002: Local Role Override via `.agent/ACTIVE_ROLE.local`
- **Date:** 2026-10-17
- **Status:** APPROVED
- **Context:**
  Team members clone the repository and need to work under their specific role (`project-lead`, `website-developer`, `ai-backend-developer`) without repeatedly creating git conflicts or overwriting each other's tracked active role file.
- **Decision:**
  Implement a two-tier role detection mechanism:
  1. `.agent/ACTIVE_ROLE.local` is added to `.gitignore`. When present on a developer's machine, it takes highest precedence.
  2. `.agent/ACTIVE_ROLE` is tracked in git and acts as the shared default (`project-lead`).
- **Consequences:**
  - Eliminates merge conflicts related to role selection.
  - Allows each developer's coding assistant to cleanly adopt their specific role persona automatically.
