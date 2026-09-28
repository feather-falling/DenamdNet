# 🏥 DemandNet: BRICS Smart Health & Supply Chain Resilience Platform

> **An intelligent, cross-border multi-horizon demand forecasting, disease outbreak surveillance, and deterministic inventory redistribution network for primary healthcare facilities across BRICS nations.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue.js-3.5%2B-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?logo=pytorch&logoColor=white)](https://pytorch.org/)
[![LightGBM](https://img.shields.io/badge/LightGBM-4.0%2B-brightgreen)](https://lightgbm.readthedocs.io/)
[![Flower FL](https://img.shields.io/badge/Flower_FL-1.4%2B-ff69b4)](https://flower.ai/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 1. Problem Statement

Primary Health Centres (PHCs) are the first line of defense for public health in emerging economies. Across BRICS member nations (India, Brazil, South Africa, China, and Russia), decentralized rural and semi-urban health clinics suffer from recurring operational failures:

1. **Unpredictable Demand Surges:** Seasonal epidemics (e.g., Dengue, Malaria, respiratory infections) trigger rapid 300–500% localized demand spikes, depleting essential stock within hours.
2. **Censored Consumption Traps:** Standard logistics forecasting tools rely solely on historical dispensing logs. When a clinic runs out of stock, recorded consumption drops to zero—causing conventional models to falsely predict *zero demand* exactly when shortage is critical.
3. **Siloed National Telemetry & Privacy Constraints:** Cross-border health intelligence sharing is blocked by strict data sovereignty laws; patient data cannot leave national borders.
4. **Supply Chain Inertia & Waste:** Medical stockpiles sit expiring in well-funded urban clinics while nearby rural facilities experience life-threatening stockouts. Centralized restocking depots often have lead times of 7–14 days.

---

## 💡 2. Solution Overview

**DemandNet** solves these structural bottlenecks through an integrated, closed-loop machine learning, clinical surveillance, and resource redistribution architecture:

* **Unbiased Quantile Demand Forecasting:** Deploys a multi-horizon LightGBM quantile regression engine (P10, P50, P90) across a 7-day planning window, incorporating censored demand unbiasing and 59 leak-free features.
* **Synchronized Outbreak Surveillance:** A multi-layered anomaly detector (MAD Residual Z-Score, CUSUM drift, Isolation Forest) coupled with a multi-resource pattern detector that correlates multi-medicine demand spikes (e.g., Paracetamol + ORS + Saline + Rapid Kits) into clinical early warnings.
* **Privacy-Preserving Federated Learning (FedProx):** Trains global deep representations across sovereign nodes in India, Brazil, and South Africa via Flower FL and proximal regularization, guaranteeing that zero raw patient or inventory telemetry ever leaves its country of origin.
* **Deterministic Two-Phase Redistribution Engine:** A graph-based proximity optimization engine that resolves shortages by transferring transferable surpluses from nearby donor clinics while strictly enforcing donor safety stock protection and physical inventory conservation.
* **Production-Grade Operational System:** Backed by an asynchronous FastAPI backend, PostgreSQL relational persistence, JWT authentication, and an interactive Vue 3 geospatial intelligence dashboard.

---

## 🌟 3. Key Features

* 📊 **Multi-Horizon Probabilistic Forecaster:** 7-day forward forecasts outputting lower-bound (P10), expected (P50), and surge-protection (P90) quantiles.
* 🚨 **Outbreak Early Warnings:** Automated detection of synchronized clinical anomalies (e.g., `DENGUE_LIKE`, `RESPIRATORY_OUTBREAK`) before official epidemiological verification.
* 🔄 **Strict Inventory Conservation:** Mathematical enforcement guarantees zero phantom units created or destroyed:
  $$\text{Closing Stock}_t = \text{Opening Stock}_t + \text{Received}_t + \text{Incoming Transfers}_t - \text{Consumed}_t - \text{Outgoing Transfers}_t$$
* 🛡️ **Donor Safety Protection:** Guarantees donor facilities never risk stockouts by protecting 7 days of forecasted consumption plus safety buffer stock before calculating transferable surplus.
* 🗺️ **Geodesic Nearest-Neighbor & BFS Routing:** Evaluates top-5 nearest facilities via Haversine distance, falling back to cycle-free Breadth-First Search (BFS) graph expansion.
* 🔐 **Privacy-Preserving FedProx:** Cross-country federated aggregation with non-IID drift mitigation via proximal penalty terms.
* 🖥️ **Role-Based PHC Community Portal:** Secure PHC authentication with JWT, enabling facility heads to raise, review, approve, and track peer-to-peer medicine transfers in real-time.

---

## 🏛️ 4. System Architecture

```mermaid
flowchart TB
    subgraph S_DATA["1. Primary Healthcare Facilities & Telemetry Layer"]
        PHC["271 Canonical PHCs<br/>(India: 54, Brazil: 54, South Africa: 55, China: 54, Russia: 54)"]
        TELEM["Daily Telemetry Ingestion<br/>(Stock, Consumption, Inflow, Outflow, Footfall, Staff)"]
        PHC --> TELEM
    end

    subgraph S_CORE["2. DemandNet Machine Learning & Surveillance Pipeline"]
        TELEM --> RECON["Stock Reconciliation & Unbiasing<br/>(is_censored = 1 if stock == 0)"]
        RECON --> FEAT["Leak-Free Feature Builder (59 Features)<br/>- Cyclical Temporal (Sin/Cos)<br/>- Rolling Demand Lags (t-1, t-7, t-14, t-28)<br/>- Stock Cover Days & Peer Momentum"]
        FEAT --> L_ML["Multi-Horizon Quantile Forecaster<br/>(LightGBM P10, P50, P90 across 7 Horizons)"]
        FEAT --> L_ANO["Layered Anomaly Detector<br/>(MAD Residual Z-Score + CUSUM + Isolation Forest)"]
        FEAT --> L_PAT["Multi-Resource Outbreak Detector<br/>(Cross-Resource Correlation Spikes)"]
        L_ML & L_ANO --> RISK["Stockout Depletion & Risk Engine<br/>(Days to Stockout, Safety Stock Deficits)"]
    end

    subgraph S_FED["3. Cross-Country Federated Learning (FedProx)"]
        direction TB
        C_IN["India FL Node"] & C_BR["Brazil FL Node"] & C_ZA["South Africa FL Node"]
        AGG["Global FedProx Server<br/>Aggregates Parameter Weights w_i"]
        C_IN & C_BR & C_ZA <-->|Weights w_i only| AGG
    end

    subgraph S_REDIST["4. Deterministic Redistribution Engine"]
        L_PAT -->|Outbreak Signals| ALERTS["outputs/alerts/alerts.json"]
        RISK -->|Sharma Contract Data| PREDS["outputs/predictions/predictions.json"]
        ALERTS & PREDS --> SOLVER["Two-Phase Proximity Solver<br/>- Phase 1: Top-5 Nearest Neighbors<br/>- Phase 2: BFS Network Graph Search"]
        SOLVER --> OUTPUTS["Rebalanced Allocations<br/>- redistribution_results.json<br/>- next_day_phc_data.json<br/>- unresolved_requirements.json"]
    end

    subgraph S_APP["5. Operational Backend & Frontend Dashboard"]
        OUTPUTS --> API["FastAPI Operational Backend<br/>(PostgreSQL Relational DB + JWT Auth)"]
        API --> UI["Vue 3 Geospatial Intelligence Dashboard<br/>(Interactive Mapbox/Leaflet Maps, ECharts Envelopes, PHC Portal)"]
    end
```

---

## 🔁 5. End-to-End Technical Workflow

```mermaid
sequenceDiagram
    autonumber
    actor Officer as District Health Officer / PHC Admin
    participant Input as Daily Telemetry Ingestion
    participant Forecaster as DemandNet Forecaster
    participant Surveillance as Outbreak Pattern Detector
    participant Engine as Redistribution Engine
    participant Backend as FastAPI / PostgreSQL
    participant Dashboard as Vue 3 GIS Dashboard

    Officer->>Input: Submit Daily Telemetry (input_today.json)
    Input->>Forecaster: Provide Reconciled Stock & Historical Features
    par Parallel ML Execution
        Forecaster->>Forecaster: Compute Multi-Horizon P10, P50, P90 Quantiles
        Forecaster->>Surveillance: Forward Residual Demand Spikes
        Surveillance->>Surveillance: Screen Multi-Item Correlations (Dengue, Respiratory)
    end
    Forecaster-->>Backend: Store predictions.json (Sharma Redistribution Contract)
    Surveillance-->>Backend: Store alerts.json (Clinical Early Warning Alerts)
    Officer->>Engine: Run Daily Redistribution Run
    Engine->>Backend: Fetch Active Predictions, Alerts, and Facilities Network
    Engine->>Engine: Filter Priority Alert Targets & HIGH Risk Facilities
    Engine->>Engine: Compute Transferable Surpluses under Donor Protection Law
    Engine->>Engine: Execute Nearest-Neighbor & BFS Routing Allocations
    Engine-->>Backend: Save redistribution_results.json & next_day_phc_data.json
    Backend-->>Dashboard: Stream Updated Network Status & Transfer Graph
    Dashboard-->>Officer: Render Geospatial Routes, Risk Heatmap & Transfer Dispatches
```

---

## 📈 6. Demand Forecasting Pipeline

```mermaid
flowchart LR
    A["Raw Facility Data<br/>(Inventory & Footfall)"] --> B["Stock Reconciliation<br/>& Censoring Flag"]
    B --> C["59 Temporal & Spatial Features<br/>- Lags: t-1, t-7, t-14, t-28<br/>- Rolling EWMA, Mean, Std<br/>- Patient Footfall Velocity"]
    C --> D["Model Evaluation Ladder<br/>1. Seasonal Naive<br/>2. 7-Day Moving Average<br/>3. LightGBM Quantile (21 Trees)<br/>4. DemandNet GRU+Tabular"]
    D --> E["Probabilistic Quantile Forecast<br/>- P10: Anti-Hoarding Bound<br/>- P50: Baseline Planning<br/>- P90: Surge & Safety Stock"]
    E --> F["Stockout Depletion Calculus<br/>Find Horizon d* where:<br/>sum(P50) >= Current Stock"]
    F --> G["Sharma Contract Record<br/>Risk Category: HIGH / MED / LOW"]
```

### Unbiased Censored Demand Estimation
When inventory reaches zero ($\text{Closing Stock}_t = 0$), recorded patient consumption drops to zero regardless of real community demand. To prevent models from learning false zero-demand trends:
1. `StockReconciler` detects stockout conditions and flags `is_censored = 1`.
2. Features incorporate rolling censored fractions over 14-day intervals.
3. The forecaster evaluates pinball loss weighted towards true underlying patient visits.

### Multi-Horizon Pinball Loss Function
For horizon $h \in \{1 \dots 7\}$ and quantile $\tau \in \{0.10, 0.50, 0.90\}$, the objective minimizes:
$$L_\tau(y, \hat{y}) = \max(\tau(y - \hat{y}), (1 - \tau)(\hat{y} - y))$$

---

## 🔍 7. Anomaly Detection & Outbreak Surveillance

The surveillance subsystem combines statistical process control with machine learning:

1. **Robust Residual Z-Score Detector:** Computes Median Absolute Deviation (MAD) on residual errors $(y - \hat{y}_{\text{P50}})$. Eliminates Gaussian distribution sensitivity:
   $$\text{Z-Score} = \frac{0.6745 \cdot (r - \text{median}(r))}{\text{MAD}(r)}$$
2. **Cumulative Sum (CUSUM) Detector:** Tracks cumulative positive deviations to detect gradual, emerging disease transmission before peak surges occur.
3. **Isolation Forest Outlier Detector:** Identifies multi-dimensional operational anomalies across combined demand, stock cover, and staff absenteeism.
4. **Multi-Resource Pattern Detector:** Correlates simultaneous anomalies across co-used medical supplies. When antipyretics, oral rehydration salts, IV fluids, and diagnostic rapid kits surge concurrently at a PHC, the system triggers a **`DENGUE_LIKE`** emergency alert.

---

## 🌐 8. Federated Learning Architecture (FedProx)

```mermaid
flowchart TD
    subgraph Central_Coordinator["Central Federation Coordinator"]
        GLOBAL["Global DemandNet Model (w^t)"]
        AGG["FedProx Aggregator<br/>min sum(n_i/N * L_i) + (μ/2)||w - w^t||^2"]
        GLOBAL --> AGG
    end

    subgraph IN_Sovereign["India Sovereign Node"]
        IN_DATA[("National Health Telemetry<br/>54 PHCs (In-Country)")]
        IN_CLIENT["Flower Client 1<br/>Local Training"]
        IN_DATA --- IN_CLIENT
    end

    subgraph BR_Sovereign["Brazil Sovereign Node"]
        BR_DATA[("National Health Telemetry<br/>54 PHCs (In-Country)")]
        BR_CLIENT["Flower Client 2<br/>Local Training"]
        BR_DATA --- BR_CLIENT
    end

    subgraph ZA_Sovereign["South Africa Sovereign Node"]
        ZA_DATA[("National Health Telemetry<br/>55 PHCs (In-Country)")]
        ZA_CLIENT["Flower Client 3<br/>Local Training"]
        ZA_DATA --- ZA_CLIENT
    end

    GLOBAL -->|1. Broadcast Global Weights w^t| IN_CLIENT
    GLOBAL -->|1. Broadcast Global Weights w^t| BR_CLIENT
    GLOBAL -->|1. Broadcast Global Weights w^t| ZA_CLIENT

    IN_CLIENT -->|2. Local Parameter Weights w_1| AGG
    BR_CLIENT -->|2. Local Parameter Weights w_2| AGG
    ZA_CLIENT -->|2. Local Parameter Weights w_3| AGG

    AGG -->|3. Updated Global Weights w^(t+1)| GLOBAL
```

### Data Sovereignty Preservation
Cross-border transfer of individual patient encounters or facility stock records violates national healthcare privacy legislation. DemandNet leverages [Flower](https://flower.ai/) to orchestrate local training on national servers. Only encrypted model parameter gradients are exchanged with the coordinator.

### FedProx Non-IID Regularization
To prevent client drift across disparate healthcare infrastructures, the FedProx strategy introduces a proximal regularization term:
$$\min_{\mathbf{w}} \sum_{i=1}^K \frac{n_i}{N} \mathcal{L}_i(\mathbf{w}) + \frac{\mu}{2} \|\mathbf{w} - \mathbf{w}^t\|^2$$
where $\mu = 0.01$ stabilizes training under extreme epidemiological heterogeneity.

---

## 🚚 9. Medicine Redistribution & Coordination Engine

```mermaid
flowchart TD
    START["Start Redistribution Solver"] --> INGEST["Ingest predictions.json & alerts.json"]
    INGEST --> FILTER["Filter Deficit Targets<br/>- Priority 1: Clinical Alert Facilities<br/>- Priority 2: Risk Score >= 0.7 (HIGH)"]
    FILTER --> DEFICIT["Compute Net Required Transfer Units<br/>Target Deficit = (7d Demand + Safety Stock) - Current Stock"]
    DEFICIT --> GEO["Inspect Facility Geodesic Distances (Haversine)"]

    subgraph Allocation_Loop["Two-Phase Search & Donor Protection"]
        GEO --> P1["Phase 1: Top-5 Nearest Neighbors"]
        P1 -->|Check Donor| SURPLUS{"Transferable Surplus > 0?<br/>Surplus = Stock - (7d Demand + Safety Stock)"}
        SURPLUS -->|Yes| TRANSFER["Allocate Multi-Source Transfer<br/>Transfer = min(Deficit, Surplus)"]
        SURPLUS -->|No / Exhausted| P2["Phase 2: BFS Graph Expansion<br/>(Cycle Detection + Geodesic Distance Sorting)"]
        P2 -->|Candidate Found| SURPLUS
        P2 -->|Network Exhausted| UNRESOLVED["Record in unresolved_requirements.json"]
    end

    TRANSFER --> UPDATE_STATE["Update GlobalInventoryState<br/>(Instant In-Memory Balance Adjustments)"]
    UPDATE_STATE --> COMPLETE{"Target Deficit Resolved?"}
    COMPLETE -->|No| P1
    COMPLETE -->|Yes| NEXT["Export Results<br/>- redistribution_results.json<br/>- next_day_phc_data.json"]
```

### Donor Protection Law
A donor clinic must never be depleted into a deficit state to supply another facility. Transferable surplus is strictly constrained:
$$\text{Protected Stock} = (\text{Daily Demand} \times 7) + \text{Safety Stock}$$
$$\text{Transferable Surplus} = \max(0, \text{Current Stock} - \text{Protected Stock})$$

### Shared In-Memory Global State
The `GlobalInventoryState` tracks real-time inventory balances across the entire network during execution. When Donor $A$ transfers 150 units to Target $B$, Donor $A$'s balance is decremented immediately, guaranteeing that stock cannot be double-allocated to subsequent targets.

---

## 📊 10. Data & Provenance Architecture

DemandNet supports **271 canonical primary health facilities** across five countries, each cataloged with real-world administrative classifications, geographic coordinates, and 18 essential medical supplies:

| Country | Facilities | Administrative Division | Essential Items | Catalog Path |
| :--- | :---: | :--- | :---: | :--- |
| **India** 🇮🇳 | 54 PHCs | 10 States / 18 Districts | 18 | `data/india/` |
| **Brazil** 🇧🇷 | 54 PHCs | 5 Regions / 15 States | 18 | `data/brazil/` |
| **South Africa** 🇿🇦 | 55 PHCs | 9 Provinces / 16 Districts | 18 | `data/south_africa/` |
| **China** 🇨🇳 | 54 PHCs | 6 Regions / 14 Provinces | 18 | `data/china/` |
| **Russia** 🇷🇺 | 54 PHCs | 7 Federal Districts / 16 Oblasts | 18 | `data/russia/` |
| **Total** | **271 PHCs** | **Full BRICS Coverage** | **18 Items** | **`data/`** |

> [!IMPORTANT]
> **Data Leakage Protection:**
> Simulation scenarios and ground truth (`events.json`) are strictly decoupled from operational inputs. The ML models and redistribution solver receive only operational telemetry (`input_today.json`), ensuring zero synthetic leakage.

---

## ⚙️ 11. Backend & Operational API Architecture

The backend is built with **FastAPI** and uses **SQLAlchemy ORM** connecting to **PostgreSQL** with connection pooling and thread-safe sessions.

### API Endpoints Overview

| Method | Endpoint | Description | Access |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Server and system health status | Public |
| `POST` | `/api/run-daily` | Launch end-to-end daily pipeline (ML + Redistribution) | Public |
| `GET` | `/api/run-daily/status/{job_id}` | Poll asynchronous daily orchestration progress | Public |
| `GET` | `/api/results/summary` | Query aggregate multi-country transfer & resolution metrics | Public |
| `GET` | `/api/predictions` | Query Sharma contract forecasts with filter params | Public |
| `GET` | `/api/alerts` | Query active disease & outbreak early warning alerts | Public |
| `POST` | `/api/redistribution/run` | Execute standalone network redistribution solver | Public |
| `GET` | `/api/redistribution/results` | Retrieve complete transfer orders and routing breakdown | Public |
| `GET` | `/api/phcs/{phc_id}` | Facility master record & geospatial metadata | Public |
| `GET` | `/api/phcs/{phc_id}/inventory` | Live operational inventory levels and risk scores | Public |
| `POST` | `/api/auth/register` | Register new PHC account with bcrypt password hashing | Public |
| `POST` | `/api/auth/login` | Authenticate PHC user and generate signed JWT | Public |
| `GET` | `/api/auth/me` | Retrieve authenticated user profile | Bearer JWT |
| `POST` | `/api/requests` | Raise emergency peer-to-peer medicine request | Bearer JWT |
| `GET` | `/api/requests` | List open peer requests across district | Bearer JWT |
| `POST` | `/api/requests/{id}/approve` | Donor PHC approves and supplies peer request | Bearer JWT |

---

## 🗄️ 12. Database Architecture

The relational PostgreSQL schema (`brics_health`) provides reliable state management for community interactions:

```mermaid
erDiagram
    PHC_ACCOUNTS ||--o{ OPERATIONAL_REQUESTS : "initiates (as requester)"
    PHC_ACCOUNTS ||--o{ OPERATIONAL_REQUESTS : "supplies (as donor)"

    PHC_ACCOUNTS {
        uuid id PK
        string phc_name
        string email UK
        string password_hash
        string country
        string assigned_phc_id
        datetime created_at
        datetime updated_at
    }

    OPERATIONAL_REQUESTS {
        uuid id PK
        uuid requester_phc_id FK
        string medicine_id
        string medicine_name
        integer quantity
        string urgency
        string status
        text reason
        uuid supplied_by_phc_id FK
        integer supplied_quantity
        text response_notes
        datetime created_at
        datetime updated_at
    }
```

* **Connection Pooling:** Configured with `pool_pre_ping=True`, `pool_size=10`, and `max_overflow=20` for resilience against connection drops.
* **Graceful Standalone Fallback:** If PostgreSQL is offline, `backend/storage/json_store.py` ensures the entire forecasting and redistribution pipeline continues to operate via JSON persistence.

---

## 💻 13. Frontend Dashboard

Built with **Vue 3**, **Vite**, **TypeScript**, and **TailwindCSS**:

* **Geospatial Command Map:** Leaflet & Mapbox GL vector visualization of all 271 PHCs with dynamic clustering, risk heatmaps, and animated transfer delivery corridors.
* **Probabilistic Forecast Envelopes:** Interactive ECharts displaying multi-horizon P10–P50–P90 confidence bands for each facility and medicine.
* **Outbreak Early Warning Feed:** Real-time alert monitor detailing disease patterns, confidence scores, correlated items, and clinical intervention protocols.
* **PHC Community Portal:** Modal-driven interface for facility officers to request stock, inspect regional surplus availability, and execute peer-to-peer transfers.

---

## 📂 14. Project Directory Structure

```text
Bricks/
├── package.json                    # Root scripts (concurrent frontend & backend)
├── requirements.txt                # Curated Python dependencies (ML, API, DB, Testing)
├── run_daily.py                    # Master CLI orchestration runner
├── verify_phcs.py                  # Canonical validation script for all 271 PHCs
├── .env.example                    # Backend environment configuration template
├── .gitignore                      # Git exclusion rules (secrets, venv, caches)
├── input/
│   └── input_today.json            # Active multi-country daily operational telemetry
├── inputs/
│   ├── daily_input_template.json   # Template for entering daily facility reports
│   └── input_today.json            # Operational input mirror
├── output/                         # Primary generated operational outputs
│   ├── alerts/
│   │   ├── alerts.json             # Outbreak early warning alerts
│   │   └── predictions.json        # Next-day forecasts (Sharma Contract)
│   └── redistribution/
│       ├── next_day_phc_data.json  # Rebalanced inventory state for next day
│       ├── redistribution_results.json # Full transfer orders and routing summary
│       └── unresolved_requirements.json# Unresolved deficits log
├── data/                           # Canonical datasets for BRICS nations
│   ├── india/                      # 54 PHCs, 18 medicines, 365-day timeseries, topology
│   ├── brazil/                     # 54 PHCs, 18 medicines, 365-day timeseries, topology
│   ├── south_africa/               # 55 PHCs, 18 medicines, 365-day timeseries, topology
│   ├── china/                      # 54 PHCs, 18 medicines, 365-day timeseries, topology
│   └── russia/                     # 54 PHCs, 18 medicines, 365-day timeseries, topology
├── ai-ml/                          # DemandNet Machine Learning Subsystem
│   ├── run_daily_prediction.py     # Standalone daily ML prediction runner
│   ├── main.py                     # 12-phase pipeline benchmark & evaluation runner
│   ├── config.yaml                 # ML hyperparameters & feature definitions
│   ├── schemas/                    # JSON schema definitions (prediction_schema.json)
│   ├── preprocessing/              # Loaders, stock reconciler, time splitter
│   ├── features/                   # 59 leak-free feature extractors
│   ├── models/                     # LightGBM, DemandNet GRU, Anomaly & Pattern Detectors
│   ├── federated/                  # Flower FL client, FedProx strategy, federation simulator
│   ├── inference/                  # Prediction service conforming to Sharma Contract
│   ├── simulation/                 # Closed-loop evaluation simulator
│   └── tests/                      # Automated unit test suite (9 tests)
├── redistribution/                 # Resource Redistribution Subsystem
│   ├── run_redistribution.py       # Standalone redistribution CLI
│   ├── engine/                     # Target identification, candidate search, transfer logic
│   ├── models/                     # In-memory dataclasses (GlobalInventoryState, etc.)
│   └── utils/                      # Haversine distance, network loaders
├── backend/                        # Operational FastAPI Backend
│   ├── main.py                     # FastAPI application & route mounting
│   ├── config.py                   # Pydantic environment settings
│   ├── api/                        # Modular API routers (health, alerts, daily, phcs, etc.)
│   ├── auth/                       # Security utilities (bcrypt hashing, JWT creation/decoding)
│   ├── db/                         # SQLAlchemy connection & ORM models (PHCAccount, Request)
│   ├── schemas/                    # Pydantic schemas for request/response serialization
│   ├── services/                   # Business logic (pipeline orchestrator, redistribution)
│   └── storage/                    # File-based JSON fallback persistence
├── Frontend/                       # Vue 3 Geospatial Dashboard
│   ├── package.json                # Frontend dependencies (Vue 3, Vite, Tailwind, ECharts)
│   ├── vite.config.ts              # Vite configuration
│   ├── src/
│   │   ├── pages/hospital/         # BricsResultsDashboard.vue
│   │   ├── components/             # Reusable UI cards, maps, modals, charts
│   │   ├── lib/                    # Geodesic mapbox & general TypeScript utilities
│   │   └── App.vue                 # Application root
├── simulation/                     # Telemetry Generation & Synthetic Stress Engine
│   ├── generator.py                # Daily telemetry synthesizer with inventory conservation
│   └── generate_daily_input.py     # CLI tool to simulate arbitrary test days
└── tests/                          # Master Integration Test Suite (39 tests)
    ├── test_alerts_processing.py   # Clinical alert verification
    ├── test_backend_api.py         # FastAPI TestClient endpoint integration tests
    ├── test_deterministic_scenario.py # Deterministic scenario validations
    ├── test_distance.py            # Haversine distance accuracy
    ├── test_integrated_system.py   # Full pipeline integration tests
    ├── test_inventory_conservation.py # Mathematical conservation law verification
    ├── test_neighbor_search.py     # Proximity and BFS search tests
    ├── test_outputs.py             # Output schema compliance
    ├── test_source_surplus.py      # Donor protection calculations
    ├── test_target_calculation.py  # Deficit and urgency calculations
    └── test_transfers.py           # Multi-source transfer execution
```

---

## 🧪 15. Experimental Results & Verification

All automated unit, integration, and scenario tests are verified and passing:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.0.2
collected 39 items

tests\test_alerts_processing.py ...                                      [  7%]
tests\test_backend_api.py .......                                        [ 25%]
tests\test_deterministic_scenario.py ..                                  [ 30%]
tests\test_distance.py ...                                               [ 38%]
tests\test_integrated_system.py .....                                    [ 51%]
tests\test_inventory_conservation.py ...                                 [ 58%]
tests\test_neighbor_search.py ...                                        [ 66%]
tests\test_outputs.py ..                                                 [ 71%]
tests\test_source_surplus.py ....                                        [ 82%]
tests\test_target_calculation.py ...                                     [ 89%]
tests\test_transfers.py ....                                             [100%]

======================== 39 passed in 7.11s ==================================
```

```text
========================= ai-ml test session starts ===========================
collected 9 items

ai-ml\tests\test_closed_loop.py .                                        [ 11%]
ai-ml\tests\test_daily_pipeline.py ...                                   [ 44%]
ai-ml\tests\test_data.py .                                               [ 55%]
ai-ml\tests\test_features.py .                                           [ 66%]
ai-ml\tests\test_models.py ..                                            [ 88%]
ai-ml\tests\test_predictions.py .                                        [100%]

========================= 9 passed in 32.28s ==================================
```

```text
> python verify_phcs.py
Canonical Counts: India=54, Brazil=54, South Africa=55, China=54, Russia=54, Total=271
All 271 canonical PHC coordinates and countries verified successfully across 5 countries!
```

---

## 🚀 16. Installation & Setup

### Prerequisites
* **Python 3.10+**
* **Node.js 18+ & npm**
* **PostgreSQL 14+** (Optional: application automatically uses JSON storage fallback if database is not running)

### 1. Clone the Repository
```bash
git clone https://github.com/feather-falling/DenamdNet.git
cd DenamdNet
```

### 2. Python Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# Install all project dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd Frontend
npm install
cd ..
```

### 4. Environment Configuration
Copy the template configuration files:
```bash
# Root backend configuration
copy .env.example .env      # Windows
# cp .env.example .env      # Linux/macOS

# Frontend configuration
copy Frontend\.env.example Frontend\.env  # Windows
# cp Frontend/.env.example Frontend/.env  # Linux/macOS
```

Edit `.env` to configure your PostgreSQL connection and JWT secret if running with a live database:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/brics_health
JWT_SECRET=your_secure_random_jwt_secret_key_here
PORT=8000
HOST=0.0.0.0
```

---

## ⚡ 17. Running the System

### Option A: Concurrent Development Mode (Frontend + Backend)
Run both services with a single command from the project root:
```bash
npm run dev
```
* **Frontend Dashboard:** `http://localhost:5173`
* **FastAPI Backend:** `http://localhost:8000`
* **Swagger API Documentation:** `http://localhost:8000/docs`

---

### Option B: Standalone Services

#### 1. Start Backend API Server
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Start Frontend Dev Server
```bash
cd Frontend
npm run dev
```

---

### Option C: CLI Operational Workflows

#### 1. Run Complete Daily Orchestration Pipeline
Executes daily telemetry simulation, ML multi-horizon forecasting, anomaly detection, and redistribution in one command:
```bash
python run_daily.py --country india
```
*Add `--country all` to evaluate all 271 facilities across BRICS nations simultaneously.*

#### 2. Run Standalone Daily ML Prediction
```bash
python ai-ml/run_daily_prediction.py --input input/input_today.json
```

#### 3. Run Standalone Redistribution Engine
```bash
python redistribution/run_redistribution.py --country india
```

#### 4. Run Automated Test Suites
```bash
# Run backend and redistribution tests (39 tests)
python -m pytest tests --ignore=tests/test_live_api.py

# Run AI-ML model and pipeline tests (9 tests)
python -m pytest ai-ml/tests

# Verify facility catalogs and coordinates (271 PHCs)
python verify_phcs.py
```

---

## 🛠️ 18. Technology Stack

| Domain | Technology / Library | Purpose |
| :--- | :--- | :--- |
| **Machine Learning** | LightGBM | Multi-horizon quantile regression (P10, P50, P90) |
| **Deep Learning** | PyTorch | DemandNet GRU sequence encoder + Tabular embeddings |
| **Federated Learning** | Flower (`flwr`) | Cross-border FedProx model aggregation |
| **Data & Feature Engineering** | Pandas, NumPy, SciPy | Leak-free lag matrices, rolling EWMA, MAD statistics |
| **API & Server** | FastAPI, Uvicorn | High-performance asynchronous REST endpoints |
| **Relational Database** | PostgreSQL, SQLAlchemy | ORM persistence, connection pooling, migrations |
| **Authentication & Security** | PyJWT, bcrypt | Salted password hashing & signed token validation |
| **Frontend Framework** | Vue 3, Vite, TypeScript | Modern reactive UI architecture |
| **Styling & Components** | TailwindCSS, Radix Vue | Design system & accessible UI primitives |
| **Visualizations** | Apache ECharts, Leaflet, Mapbox GL | Geospatial routing maps & quantile envelope charts |
| **Automated Testing** | Pytest, HTTPX | Unit, integration, and API test coverage |

---

## 🔐 19. Security & Secret Handling

* **No Plaintext Passwords:** User credentials are encrypted using `bcrypt` with 12 rounds of cryptographic salting before database insertion.
* **Stateless Authorization:** Authenticated routes enforce signed HS256 JWT tokens with configurable expiration windows.
* **Environment Isolation:** All secret keys, database connection strings, and access tokens are loaded via `.env` and strictly excluded from version control via `.gitignore`.
* **Zero Patient Data Leakage:** Federated training guarantees that only model weights are transmitted across national borders.

---

## ⚠️ 20. Limitations

DemandNet is currently a hackathon-stage prototype designed to demonstrate the feasibility of an end-to-end intelligent healthcare supply-chain coordination system.

* **Synthetic Operational Telemetry:** PHC facility metadata, geographic information, and medicine catalogs are based on public/reference data where available, while daily inventory, consumption, and operational telemetry are synthetically generated for controlled experimentation and hackathon evaluation.
* **Prototype-Scale Deployment:** The current implementation is validated on a controlled multi-country dataset and simulated federated environment rather than live national healthcare infrastructure.
* **Road Network Approximation:** Redistribution currently uses Haversine geodesic distance and graph-based routing. Integration with real road-network services would allow routing to account for road conditions, travel time, terrain, and transport constraints.
* **Cold-Chain Logistics:** Current transfer validation focuses on inventory quantities, facility proximity, and donor protection. Temperature-controlled transport and continuous cold-chain monitoring are not yet modeled.
* **Clinical Validation:** Outbreak detection produces computational early-warning signals such as `DENGUE_LIKE` and `RESPIRATORY_OUTBREAK`; these signals are not clinical diagnoses and would require validation against official epidemiological surveillance systems before operational deployment.
* **Federated Deployment:** The current federated-learning environment demonstrates cross-country training using simulated sovereign nodes. Production deployment would require integration with authorized national health infrastructure, secure aggregation, governance controls, and formal privacy/security audits.

---

## 🔮 21. Future Scope

* **Multimodal Drone & Cold-Chain Routing:** Integrating dynamic route planning with vehicle payload and temperature logger telemetry.
* **Automated Supplier Re-Ordering:** Extending redistribution output directly into national public procurement systems (e.g., India's GeM / e-Aushadhi).
* **LLM Clinical Assistant:** Fine-tuning an on-device clinical assistant to help rural nurses triage symptoms during emerging outbreak alerts.

---

## 👥 22. Team & Responsibilities

Developed as a collaborative project for the **BRICS Smart Health & Supply Chain Resilience Initiative**.

| Team Member | Role | Primary Responsibility |
| :--- | :--- | :--- |
| **Aryan Prajapati** | **Lead Developer & Project Coordinator** | Overall system architecture, data collection & preparation, core implementation, ML/FL integration, pipeline orchestration, testing, technical coordination, and end-to-end system development |
| **Anant** | **AI/ML Engineer** | Machine learning pipeline, demand forecasting, feature engineering, anomaly detection, and federated learning research |
| **Aryan Sharma** | **Redistribution Engine Engineer** | Medicine redistribution logic, donor-protection constraints, proximity search, transfer allocation, and inventory balancing |
| **Divyansh Gupta** | **Backend & Frontend Engineer** | FastAPI services, PostgreSQL integration, authentication, API integration, and Vue dashboard development |

---

## 📄 23. License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
