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

## 3. Research Contribution

This project contributes a **practical demonstration** of how classical inventory theory can be enhanced through data-driven uncertainty quantification.

The central insight is:

> **Learning demand volatility from historical data and incorporating it into safety stock calculations yields measurable improvements in fill rate and cost efficiency, without requiring complex optimization or machine learning.**

This contribution is pedagogical and methodological:
- It shows that **modeling uncertainty well** is often more valuable than adopting sophisticated algorithms
- It provides a reproducible template for simulation-based policy evaluation
- It emphasizes **decision quality under uncertainty** rather than forecasting accuracy or algorithmic novelty

The project is suitable for classroom instruction in Operations Management, demonstrating how foundational concepts (safety stock, reorder points, service levels) translate into actionable, data-informed decisions.

---

## 4. Key Modeling Decisions (Locked)

### 4.1 Decision-Maker and Setting
- Single retailer
- Multiple products (SKUs or product categories)
- Centralized inventory control
- Finite time horizon
- Lost sales (no backorders)

### 4.2 Demand Modeling Philosophy
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

## 5. Forecasting Layer (Intentionally Simple)

Forecasting accuracy is **not** the main objective.

Two forecast sources may be used:
1. Forecasts provided in the dataset (if available)
2. Simple baselines (rolling mean or exponential smoothing)

This allows the project to isolate **policy robustness** rather than optimize predictive models.

---

## 6. Inventory Policies Considered

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

## 7. Why Reinforcement Learning Is Not Used

Reinforcement Learning (RL) is intentionally excluded for the following reasons:

- **Data sparsity**: Retail datasets typically contain hundreds of time steps, far below what RL requires for stable learning.
- **Interpretability**: Classical inventory policies offer transparent decision rules understandable by managers and instructors.
- **Robustness**: Parameter-based policies are easier to recalibrate under demand regime shifts than black-box RL models.
- **Scope discipline**: The project prioritizes depth and clarity over algorithmic novelty.

---

## 8. Evaluation Methodology

### 8.1 Simulation
- Policies are evaluated using **Monte Carlo simulation**
- Each policy is tested across many stochastic demand realizations
- Performance is summarized using mean values and confidence intervals

### 8.2 Metrics (Efficiency Only)
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

## 9. Experimental Design

The simulation study is structured to isolate the effect of **uncertainty-aware policy tuning** on inventory performance.

### Policies Compared
| Policy | Description |
|--------|-------------|
| **Static (r, Q)** | Fixed reorder point and order quantity based on average demand |
| **Historical-mean** | Order quantity equals recent average demand; no safety stock adjustment |
| **Tuned (r, Q)** | Reorder point and safety stock dynamically adjusted using learned demand volatility |

### What Is Held Fixed
- Product assortment and cost parameters (holding cost, lead time)
- Forecast method (simple baseline)
- Simulation horizon and number of replications
- Lost-sales assumption (no backorders)

### What Varies
- **Demand volatility**: Simulations are run under low, medium, and high demand uncertainty scenarios
- This tests whether the tuned policy's advantage persists or grows as uncertainty increases

### Why Monte Carlo Simulation
Historical data represents only **one realized demand path** and cannot characterize the distribution of outcomes. Monte Carlo simulation:
- Generates many plausible demand scenarios from calibrated distributions
- Enables estimation of expected performance and confidence intervals
- Allows fair comparison of policies under identical stochastic conditions

This approach is standard in Operations Management research for evaluating inventory policies under uncertainty.

---

## 10. How to Interpret the Results

The output of this project is a **comparative policy analysis**, not a prediction or optimization.

### For Instructors
- Focus on **relative performance**: Does the tuned policy consistently outperform baselines across volatility levels?
- Examine **confidence intervals**: Overlapping intervals suggest the difference may not be practically significant
- Use the results to illustrate the **value of uncertainty modeling** in inventory decisions

### For Managers
- **Fill rate** indicates customer service level — higher is better
- **Holding cost** reflects capital tied up in inventory — lower is better
- **Stockout rate** measures lost sales risk — lower is better
- A policy that achieves higher fill rate with comparable or lower holding cost is operationally superior

### Robustness and Interpretability
- Results are averaged over many simulation runs to reduce noise
- Policies are classical and transparent — the decision rules can be explained and audited
- Sensitivity analysis shows whether conclusions hold under different demand volatility assumptions

---

## 11. Dataset Usage

The dataset is used **only for calibration**, not direct evaluation.

Specifically, it is used to:
- Estimate demand levels
- Estimate forecast error distributions
- Inform realistic parameter ranges

All policy comparisons are performed on **simulated demand paths**, not historical replay.

---

## 12. Project Structure

```
├── data/                   # Raw and processed datasets
├── src/                    # Core modeling logic
│   ├── preprocessing.py
│   ├── forecasting.py
│   ├── demand_uncertainty.py
│   ├── policies.py
│   ├── simulation.py
│   └── metrics.py
├── experiments/            # Experiment scripts and parameter sweeps
├── notebooks/              # Analysis and visualization notebooks
├── figures/                # Generated plots for reporting
└── README.md
```


---

## 13. Expected Outputs

- Clear comparison of inventory policies under demand uncertainty
- Quantified performance improvements from learning demand volatility
- Visualizations of inventory dynamics and uncertainty effects
- A reproducible simulation framework suitable for academic presentation

---

## 14. Guiding Principle

> **Better decisions under uncertainty do not require more complex algorithms — they require better modeling of uncertainty.**

This project reflects that principle.
