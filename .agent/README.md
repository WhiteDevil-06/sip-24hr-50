# Antigravity Instruction & Governance Directory (`.agent/`)

This directory houses the persistent, version-controlled governance system for the **Deep Learning-Based Soil Moisture Prediction for Smart Irrigation** project.

## Directory Overview

```
.agent/
├── README.md               # This documentation
├── ACTIVE_ROLE             # Tracked default active role (project-lead)
├── ACTIVE_ROLE.example     # Instructions for local developer override
├── GLOBAL_RULES.md         # Immutable Global Rules A through M
├── PHASES.md               # 10 phased project gates & acceptance criteria
├── PROJECT_STATE.md        # Current phase, ownership, verified facts, blockers
├── AGENT_REGISTRY.md       # Specialist reviewer roles & procedural protocol
├── roles/                  # Role definition contracts
│   ├── README.md           # Role governance overview
│   ├── project-lead.md     # Role A: Project Lead, AI Developer, Integration Owner
│   ├── website-developer.md# Role B: Ram Charan (Frontend Next.js)
│   └── ai-backend-developer.md # Role C: Rahul (Backend FastAPI serving)
├── agents/                 # Specialist reviewer personas & validation checklists
│   ├── README.md           # Review guidelines & procedural mode notice
│   ├── orchestrator.md     # Task coordination & scope enforcement
│   ├── planner.md          # Task breakdown & minimal diff planning
│   ├── code-reviewer.md    # Code cleanliness, standards, regression check
│   ├── test-validator.md   # Test execution, typing, linting, build verification
│   ├── security-reviewer.md# Credentials, input sanitization, safe config
│   ├── data-quality-reviewer.md # Data schema, missingness, sensor anomalies
│   ├── ml-integrity-reviewer.md # Time-series leakage, scaling, horizon alignment
│   ├── frontend-reviewer.md# Next.js, TypeScript, Recharts, responsive UI
│   ├── backend-reviewer.md # FastAPI, Pydantic, inference parity, error handling
│   ├── integration-reviewer.md # E2E contract, payload consistency, latency
│   └── documentation-reviewer.md # Sync docs, ADRs, experiment records
├── workflows/              # Standard operating procedures
│   ├── session-start.md    # Instructions discovery workflow
│   ├── implementation.md   # Incremental implementation cycle
│   ├── code-change-validation.md # Mandatory validation for meaningful changes
│   ├── bug-fix.md          # Defect isolation & regression prevention
│   ├── phase-completion.md # Formal phase closure & human approval gate
│   └── handoff.md          # Model handoff contract protocol
└── rules/                  # Subsystem rulebooks
    ├── coding-standards.md
    ├── testing-and-validation.md
    ├── data-and-ml-integrity.md
    ├── security-and-privacy.md
    ├── git-and-file-safety.md
    ├── dependency-management.md
    ├── frontend-rules.md
    ├── backend-rules.md
    └── documentation-rules.md
```

## How to Select Your Role
1. Cloned repos inherit `project-lead` by default from [ACTIVE_ROLE](file:///c:/Users/raksh/ANN/.agent/ACTIVE_ROLE).
2. To work as Ram Charan or Rahul without dirtying git, create [.agent/ACTIVE_ROLE.local](file:///c:/Users/raksh/ANN/.agent/ACTIVE_ROLE.local):
   - `website-developer`
   - `ai-backend-developer`
3. The instruction system checks `.agent/ACTIVE_ROLE.local` first, falling back to `.agent/ACTIVE_ROLE`.
