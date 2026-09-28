# ML System Technical Explanation & Architecture Tutorial

This document provides a comprehensive technical breakdown of the machine learning architecture designed for the **BRICS Health Resilience Project**.

---

## 1. Data Ingestion & Reconciliation Pipeline

### Inventory Conservation Law
Healthcare inventory data must satisfy strict conservation:
$$\text{Closing Stock}_t = \text{Opening Stock}_t + \text{Received}_t + \text{Incoming Transfers}_t - \text{Consumed}_t - \text{Outgoing Transfers}_t$$

### Unbiased Demand Censoring
When $\text{Closing Stock}_t = 0$, recorded consumption is capped by available inventory rather than true patient demand (censored demand). To prevent forecasters from underpredicting demand during stockouts, `StockReconciler` flags `is_censored = 1` whenever stock hits zero, enabling loss functions to adjust or un-censor target values.

### Chronological Purge Splitting
To prevent lookahead bias, `TimeSplitter` splits time series chronologically and introduces a 7-day purge window between train and test sets, matching the maximum forecast horizon.

---

## 2. Leak-Free Feature Engineering

All feature extractors strictly adhere to leak-free temporal principles:
- **Temporal Features:** Day of week, month, day of month, cyclical sine/cosine encodings.
- **Demand Features:** Lagged demand ($t-1, t-2, t-7, t-14, t-28$), 7/14/28-day rolling mean/std/EWMA, and 7-day trend slope using `shift(1)`.
- **Inventory Features:** Stock cover days $\left(\frac{\text{Stock}_{t-1}}{\text{Rolling Demand}_7 + \epsilon}\right)$, stockout lags, and 14-day censored demand fraction.
- **Operational Features:** Patient visit velocity, staff attendance ratio, diagnostic test counts.
- **Spatial Features:** District peer demand momentum and nearest neighbor spatial demand signals.
- **Resource Pattern Features:** Cross-resource correlation signals across co-used medical supplies.

---

## 3. Multi-Horizon Quantile Demand Forecasting

### Probabilistic Quantile Forecasting
Forecasting single point estimates (mean/median) is insufficient for health emergency planning. The system outputs three key quantiles for each horizon step $h \in \{1 \dots 7\}$:
- **P10 (Pessimistic Demand / Lower Bound):** Prevents over-ordering.
- **P50 (Expected Demand / Median):** Used for baseline planning.
- **P90 (Optimistic Demand / High Surge):** Used for safety stock & surge protection.

### Model Ladder
1. **Seasonal Naive Baseline:** $y_{t+h} = y_{t+h-7}$.
2. **Moving Average (7d) Baseline:** $y_{t+h} = \frac{1}{7} \sum_{i=1}^7 y_{t-i}$.
3. **LightGBM Quantile Regressor:** Trains 21 independent boosted trees (7 horizons $\times$ 3 quantiles) with pinball loss objectives.
4. **DemandNet PyTorch Architecture:**
   - **GRU Sequence Encoder:** Processes 28-day historical multivariate sequences.
   - **Tabular MLP Encoder:** Processes facility metadata and static features.
   - **Medicine Entity Embeddings:** Learns dense 8-dimensional representations for medical catalog items.
   - **Multi-Quantile Pinball Loss:** Minimizes Pinball Loss across P10, P50, and P90 simultaneously.

---

## 4. Layered Anomaly & Multi-Resource Outbreak Detection

### Layered Anomaly Detector
Combines three distinct statistical and machine learning algorithms:
1. **Robust Residual Z-Score Detector:** Uses Median Absolute Deviation (MAD) on residual errors $(y - \hat{y}_{P50})$.
2. **CUSUM (Cumulative Sum) Detector:** Detects persistent, gradual demand shifts over multiple consecutive days.
3. **Isolation Forest Detector:** Detects multi-dimensional operational anomalies across demand, stock levels, and staff attendance.

### Multi-Resource Pattern Detector
Outbreaks of infectious diseases (such as Dengue, Cholera, COVID-19, or Malaria) manifest as synchronized demand spikes across multiple distinct medical supplies. The pattern detector correlates anomalies across:
- Antipyretics (Paracetamol) + Hydration (ORS, IV Saline) + Diagnostic Kits (Dengue Rapid Kits) $\rightarrow$ **`DENGUE_LIKE` Outbreak Signal**.
- Antibiotics + Syringes + Diagnostics $\rightarrow$ **`RESPIRATORY_OUTBREAK` Signal**.

---

## 5. Stockout Prediction & Risk Scoring

### Stockout Depletion Estimation
Calculates cumulative projected demand using P50 predictions to find exact day $d^*$ when:
$$\sum_{k=1}^{d^*} \hat{y}_{P50, k} \ge \text{Current Stock}$$

### Operational Risk Scoring
Calculates a unified operational risk score $R \in [0, 1]$ based on stock cover days, stockout probability within 7 days, safety stock deficit, anomaly severity, and item criticality class (CRITICAL, ESSENTIAL, VITAL):
- **HIGH RISK ($R \ge 0.7$):** Emergency redistribution required.
- **MEDIUM RISK ($0.4 \le R < 0.7$):** Priority restock scheduled.
- **LOW RISK ($R < 0.4$):** Adequate inventory protection.

---

## 6. Closed-Loop Simulation Engine

The closed-loop simulator evaluates ML-guided inventory management across timesteps:
1. **Predict:** Generate 7-day multi-quantile forecasts and risk scores for all PHCs.
2. **Identify:** Group facilities into High Risk (deficit) vs Low Risk (surplus).
3. **Propose & Apply Transfers:** Transfer surplus stock to high-risk facilities while preserving safety stock buffers.
4. **Step Timestep:** Update inventory balances:
   $$\text{Closing Stock}_{t+1} = \text{Closing Stock}_t + \text{Transfers In} - \text{Transfers Out} - \text{Consumed}_{t+1}$$
5. **Evaluate:** Track total high-risk facility reduction and unmet demand mitigation over time.

---

## 7. Cross-Country Federated Learning (FedProx)

### Data Sovereignty Preservation
National health agencies in India, Brazil, and South Africa cannot share raw patient records or facility inventory data across international borders.

### FedProx Strategy
Local Flower clients (`CountryFlowerClient`) train local DemandNet models on national data and transmit only parameter weights $\mathbf{w}_i$ to the central server. `FedProxStrategy` aggregates weights while adding a proximal term penalty to handle non-IID data distribution across countries:
$$\min_{\mathbf{w}} \sum_{i=1}^K \frac{n_i}{N} L_i(\mathbf{w}) + \frac{\mu}{2} \|\mathbf{w} - \mathbf{w}^t\|^2$$

Resulting in model performance comparable to centralized training while guaranteeing 100% data privacy and sovereignty.
