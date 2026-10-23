# Role B: Website Developer

- **Owner:** Ram Charan
- **Role Identifier:** `website-developer`
- **Assigned Phase:** **Phase 7 (Website Development)**
- **External Repository Source:** `https://github.com/ramcharan-git123/Deep-Learning-Based-Soil-Moisture-Prediction-for-Smart-Irrigation`
- **Reference Files:**
  - [.agent/GLOBAL_RULES.md](file:///c:/Users/raksh/ANN/.agent/GLOBAL_RULES.md)
  - [.agent/PHASES.md](file:///c:/Users/raksh/ANN/.agent/PHASES.md) (Phase 7 Focus)
  - [.agent/PROJECT_STATE.md](file:///c:/Users/raksh/ANN/.agent/PROJECT_STATE.md)
  - [docs/API_CONTRACT.md](file:///c:/Users/raksh/ANN/docs/API_CONTRACT.md) (Frozen Contract)

---

## 1. Responsibilities & Scope

- Build the website dashboard in `frontend/` using **Next.js (App Router)**, **TypeScript**, and **Tailwind CSS**.
- Create responsive layouts, intuitive navigation, and accessible UI components.
- Implement time-series interactive charts using **Recharts**:
  - Historical soil moisture curve.
  - 24-hour predictive forecast curve (`SM_50cm` at 15-minute intervals).
- Display model metrics and compare configurations based on verified evaluation figures.
- Implement clear irrigation recommendation cards based on threshold criteria approved by Project Lead.
- Implement all 4 mandatory UI states:
  1. Loading skeleton/spinner.
  2. Empty/no-data state.
  3. Client-side input validation error state.
  4. Backend connection error state.
- Integrate with the backend exclusively through the approved API contract.
- Validate strict TypeScript typing (`tsc --noEmit`), lint clean code, and production build verification (`npm run build`).

---

## 2. Strict Prohibitions
- **No Fabricating Data:** Ram Charan must never invent model outputs or metrics.
- **Mock Data Discipline:** Mock data may only be used during UI development prior to backend availability, and it **MUST be explicitly labeled as mock data** in the UI.
- **No Backend/Model Alterations:** Ram Charan must not alter model code, training scripts, or backend serving endpoints.
- **No Premature Execution:** Must not build production features outside of Phase 7 without Project Lead sign-off.
