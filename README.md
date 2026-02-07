# Inventory Replenishment under Demand Uncertainty  
### Operations Management & Supply Chain Analytics – Amazon Project (PBL)

## 1. Project Overview

This project studies **inventory replenishment decisions under demand uncertainty** in a multi-product retail setting.  
The goal is to evaluate whether **learning demand uncertainty from data and tuning classical inventory policies** can improve operational efficiency compared to static heuristic approaches.

The project is intentionally designed to:
- Focus on **interpretable, operations-driven models**
- Avoid unnecessary algorithmic complexity
- Emphasize **decision quality under uncertainty**, not prediction accuracy alone

This work follows a **simulation-based evaluation framework** commonly used in Operations Management research.

---

## 2. Core Research Question

**How can data-driven estimation of demand uncertainty be used to improve the performance of classical inventory replenishment policies under stochastic demand, compared to static heuristics?**

We focus on operational efficiency metrics such as:
- Fill rate
- Stockout rate
- Holding cost
- Inventory turnover

The project does **not** study pricing, routing, or supply-chain network design.

---

## 3. Key Modeling Decisions (Locked)

### 3.1 Decision-Maker and Setting
- Single retailer
- Multiple products (SKUs or product categories)
- Centralized inventory control
- Finite time horizon
- Lost sales (no backorders)

### 3.2 Demand Modeling Philosophy
Historical retail data represents **one realized demand path** and cannot by itself characterize uncertainty.

Therefore:
- Historical data is used to **calibrate demand levels and forecast errors**
- **Monte Carlo simulation** is used to evaluate policies under uncertainty

Demand in simulation is modeled as:

\[
D_t = \max(0, \hat{D}_t + \epsilon_t)
\]

Where:
- \(\hat{D}_t\) is a demand forecast
- \(\epsilon_t\) is a stochastic forecast error sampled from a learned distribution

This explicitly separates:
- Forecasting
- Uncertainty modeling
- Inventory decision-making

---

## 4. Forecasting Layer (Intentionally Simple)

Forecasting accuracy is **not** the main objective.

Two forecast sources may be used:
1. Forecasts provided in the dataset (if available)
2. Simple baselines (rolling mean or exponential smoothing)

This allows the project to isolate **policy robustness** rather than optimize predictive models.

---

## 5. Inventory Policies Considered

Only **interpretable, classical policies** are used.

### Baseline Policies
1. **Static (r, Q) policy**
   - Fixed reorder point
   - Fixed order quantity

2. **Historical-mean replenishment**
   - Order quantity based on recent average demand

### Main Policy (Data-Driven)
3. **Tuned (r, Q) policy**
   - Demand volatility (\(\sigma\)) is learned from data
   - Safety stock is dynamically adjusted:
     \[
     SS = z \cdot \sigma \cdot \sqrt{L}
     \]
   - Reorder point:
     \[
     r = \mu_L + SS
     \]

This approach constitutes a **data-driven heuristic optimization**, not reinforcement learning.

---

## 6. Why Reinforcement Learning Is Not Used

Reinforcement Learning (RL) is intentionally excluded for the following reasons:

- **Data sparsity**: Retail datasets typically contain hundreds of time steps, far below what RL requires for stable learning.
- **Interpretability**: Classical inventory policies offer transparent decision rules understandable by managers and instructors.
- **Robustness**: Parameter-based policies are easier to recalibrate under demand regime shifts than black-box RL models.
- **Scope discipline**: The project prioritizes depth and clarity over algorithmic novelty.

---

## 7. Evaluation Methodology

### 7.1 Simulation
- Policies are evaluated using **Monte Carlo simulation**
- Each policy is tested across many stochastic demand realizations
- Performance is summarized using mean values and confidence intervals

### 7.2 Metrics (Efficiency Only)
The project focuses exclusively on efficiency metrics:

- **Fill Rate**
  \[
  FR = \frac{\sum_t \min(I_t, D_t)}{\sum_t D_t}
  \]

- **Stockout Rate**
  - Event-based or volume-based

- **Total Holding Cost**
  \[
  HC = \sum_t h \cdot I_t^{end}
  \]

- **Inventory Turnover**
  \[
  Turnover = \frac{\text{Total Sales}}{\text{Average Inventory}}
  \]

**Equity or fairness metrics are intentionally excluded.**

---

## 8. Dataset Usage

The dataset is used **only for calibration**, not direct evaluation.

Specifically, it is used to:
- Estimate demand levels
- Estimate forecast error distributions
- Inform realistic parameter ranges

All policy comparisons are performed on **simulated demand paths**, not historical replay.

---

## 9. Project Structure

inventory-uncertainty-pbl/
├── data/ # Raw and processed datasets
├── src/ # Core modeling logic
│ ├── preprocessing.py
│ ├── forecasting.py
│ ├── demand_uncertainty.py
│ ├── policies.py
│ ├── simulation.py
│ └── metrics.py
├── experiments/ # Experiment scripts and parameter sweeps
├── notebooks/ # Analysis and visualization notebooks
├── figures/ # Generated plots for reporting
└── README.md


---

## 10. Expected Outputs

- Clear comparison of inventory policies under demand uncertainty
- Quantified performance improvements from learning demand volatility
- Visualizations of inventory dynamics and uncertainty effects
- A reproducible simulation framework suitable for academic presentation

---

## 11. Guiding Principle

> **Better decisions under uncertainty do not require more complex algorithms — they require better modeling of uncertainty.**

This project reflects that principle.
