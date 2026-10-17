# Role A: Project Lead, AI Model Developer, and Integration Owner

- **Owner:** You (Me)
- **Role Identifier:** `project-lead`
- **Reference Files:**
  - [.agent/GLOBAL_RULES.md](file:///c:/Users/raksh/ANN/.agent/GLOBAL_RULES.md)
  - [.agent/PHASES.md](file:///c:/Users/raksh/ANN/.agent/PHASES.md)
  - [.agent/PROJECT_STATE.md](file:///c:/Users/raksh/ANN/.agent/PROJECT_STATE.md)
  - [.agent/AGENT_REGISTRY.md](file:///c:/Users/raksh/ANN/.agent/AGENT_REGISTRY.md)

---

## 1. Responsibilities & Scope

### AI & Research (Core Learning Mandate)
- Understand the IISc Berambadi dataset and its environmental variables.
- Design, inspect, and implement the data preprocessing pipeline.
- Implement and understand the Persistence (Naïve) baseline.
- Learn and implement the LSTM neural network architecture from first principles (tensors, input window shape, hidden layers, gate mechanisms, loss, optimizer, early stopping).
- Train the model, inspect learning curves, diagnose overfitting, and evaluate performance using MAE, RMSE, and R².
- Execute approved feature-configuration experiments and interpret results academically.
- Understand model limitations and defend the methodology academically.

### Integration Ownership
- Coordinate and formally approve the API contract with Rahul and Ram Charan.
- Package and supply Rahul with the approved model artifact, preprocessing scalers, and inference specifications.
- Supervise frontend and backend integration.
- Verify that deployed inference matches the training pipeline.
- Conduct end-to-end testing and prepare the final project demonstration.

---

## 2. Mandatory Learning Rule (Rule M)
When working on AI and model development phases:
- The coding assistant **MUST teach and guide** the Project Lead through each step.
- Do NOT silently write entire training scripts or dump finished models without explanation.
- Work in small, inspectable steps: explain the purpose of each mathematical operation, layer, loss function, and tensor dimension.
- Run relevant inspection commands and explain the outputs thoroughly.
- Ensure the Project Lead understands and can defend every implementation detail.

---

## 3. Strict Prohibitions
- Do not skip directly to complex architectures before the basic pipeline and Persistence baseline are validated.
- Do not claim novelty without reviewing literature and verifying empirical evidence.
- Do not allow downstream phases to begin without explicit human phase-gate approval.
