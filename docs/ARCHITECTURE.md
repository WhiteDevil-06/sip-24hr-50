# System Architecture — Smart Irrigation Prediction

## 1. System Overview
The Smart Irrigation Prediction system is designed to provide farmers and agronomists with reliable, 24-hour advance soil moisture predictions (`SM_50cm`) to make data-backed irrigation decisions.

```mermaid
graph TD
    subgraph Data Layer
        RawData["IISc Berambadi Dataset<br/>(15-min interval)"] --> Preprocess["Chronological Split & Preprocessing<br/>(Fit on Train Only)"]
        Preprocess --> ProcessedData["Processed Sequence Arrays<br/>[T, 96, Features]"]
    end

    subgraph AI & Modeling Layer - Project Lead
        ProcessedData --> Baseline["Persistence (Naïve) Baseline<br/>y_hat(t+96) = y(t)"]
        ProcessedData --> LSTM["LSTM Neural Network<br/>(Sequential Architecture)"]
        LSTM --> Eval["Comparative Evaluation<br/>(MAE, RMSE, R²)"]
        Eval --> HandoffBundle["Approved Model Artifact (.keras)<br/>+ Scaler (.pkl) + Handoff Spec"]
    end

    subgraph Serving Layer - Rahul
        HandoffBundle --> FastAPI["FastAPI Serving Application<br/>(Load Model Once at Startup)"]
        FastAPI --> Endpoints["/health<br/>/predict (Pydantic Validated)"]
    end

    subgraph Presentation Layer - Ram Charan
        Endpoints --> NextJS["Next.js App Router Dashboard<br/>(TypeScript + Tailwind CSS)"]
        NextJS --> Charts["Recharts Visualizations<br/>- Historical Curve<br/>- 24h Prediction Curve"]
        NextJS --> Recom["Irrigation Recommendation Card<br/>(Threshold-Based Guidance)"]
    end
```

## 2. Core Architectural Principles
1. **Decoupled Architecture:** The ML training pipeline, FastAPI serving backend, and Next.js frontend are strictly decoupled with clear interface boundaries.
2. **Zero In-Request Training:** The backend loads pre-trained model artifacts once at startup; no training occurs inside HTTP request handlers.
3. **Temporal Leakage Prevention:** Data splits and scalers are fitted exclusively on training sets.
4. **Strict Typed Contracts:** Communication between Frontend and Backend is mediated by strongly typed Pydantic models and TypeScript interfaces.
