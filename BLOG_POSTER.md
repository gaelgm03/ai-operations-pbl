# Inventory Replenishment Under Demand Uncertainty: A Simulation-Based Policy Comparison

---

## 1. Background & Motivation

- **Stockouts hurt.** Lost sales damage revenue and customer trust.
- **Over-stocking hurts too.** Excess inventory ties up capital and incurs holding costs.
- **Demand is uncertain.** Historical forecasts are never perfect—residuals contain signal.
- **Classical (r, Q) policies** are widely used but often rely on assumed or static σ.
- **Question:** Can we do better by *learning* uncertainty from data?

---

## 2. Research Question & Why It's Hard

- **Core question:** Does calibrating safety stock from historical forecast errors improve service level *robustly* across volatility scenarios?
- **Challenge 1:** Real demand is non-stationary; volatility shifts over time.
- **Challenge 2:** Improving fill rate typically raises holding cost—tradeoff is unavoidable.
- **Challenge 3:** Evaluation must be rigorous (Monte Carlo, confidence intervals).

---

## 3. Approach (Methods)

1. **Data:** Retail store inventory dataset with historical demand and forecasts.
2. **Calibration:** Extract forecast residuals; estimate σ via bootstrap.
3. **Demand generation:** Resample residuals to create stochastic demand paths.
4. **Volatility scaling:** Test robustness under σ × {0.5, 1.0, 1.5}.
5. **Simulation:** Inventory dynamics with **lost sales** and **lead time L = 1**.
6. **Policy evaluation:** Monte Carlo runs (n = 500+), compute mean and 95% CI.
7. **Metrics:** Fill rate, stockout event rate, average holding cost.

---

## 4. Policies Compared

| Policy | Description |
|--------|-------------|
| **Static (r, Q)** | Fixed reorder point; ignores learned σ. |
| **Tuned (r, Q)** | Reorder point includes safety stock = z × σ (learned from residuals). |

---

## 5. Results

### Headline Metrics (Baseline Volatility)

| Metric | Static (r, Q) | Tuned (r, Q) |
|--------|---------------|--------------|
| Fill Rate | ~85% | ~94–95% |
| Stockout Rate | Higher | Lower |
| Holding Cost | Lower | Higher |

> **Key tradeoff:** Tuned policy improves service at the cost of higher inventory.

---

### Figure A: Forecast Error Distribution

![Figure A: Histogram of forecast residuals used for calibration](figures/figure_a_error_hist.png)

*Caption: Distribution of historical forecast errors. Bootstrap samples from these residuals drive demand uncertainty in simulation.*

---

### Figure B: Sample Path – Demand vs. Inventory

![Figure B: Sample demand and inventory trajectory over time](figures/figure_b_sample_path.png)

*Caption: Example simulation run showing demand realization (blue) and inventory level (orange). Stockouts occur when inventory hits zero.*

---

### Figure C: Fill Rate by Volatility

![Figure C: Fill rate (mean ± 95% CI) across volatility scenarios](figures/figure_c_fill_rate.png)

*Caption: Tuned policy maintains higher fill rate across all volatility levels. Gap widens as volatility increases.*

---

### Figure D: Holding Cost by Volatility

![Figure D: Holding cost (mean ± 95% CI) across volatility scenarios](figures/figure_d_holding_cost.png)

*Caption: Tuned policy incurs higher holding cost—the classic service-level vs. cost tradeoff.*

---

## 6. Conclusion & Managerial Insight

- **Tuned (r, Q) delivers more consistent service** under demand uncertainty.
- **Robustness matters:** Tuned policy degrades less as volatility increases.
- **Tradeoff is real:** Higher fill rate → higher holding cost. Managers must choose.
- **Data-driven calibration is actionable:** No complex ML; just bootstrap + safety stock.
- **Implication:** Organizations with volatile demand benefit most from learned σ.

---

## 7. Limitations & Next Robustness Checks

- **Lost sales assumption:** Backorders would change dynamics; results may differ.
- **Fixed z:** Safety factor z is exogenous; joint optimization not explored.
- **Single SKU:** Multi-product interactions and substitution not modeled.
- **Future checks:**
  - Mis-specified σ (what if calibration is wrong?)
  - Non-Gaussian residuals (heavy tails, skewness)
  - Lead time sensitivity (L > 1)

---

## 8. Poster Layout Suggestion

```
┌─────────────────┬─────────────────┬─────────────────┐
│   COLUMN 1      │   COLUMN 2      │   COLUMN 3      │
├─────────────────┼─────────────────┼─────────────────┤
│ Title & Authors │ Results (cont.) │ Conclusion      │
│                 │                 │                 │
│ Background &    │ Figure C:       │ Managerial      │
│ Motivation      │ Fill Rate       │ Insight         │
│                 │                 │                 │
│ Research        │ Figure D:       │ Limitations     │
│ Question        │ Holding Cost    │                 │
│                 │                 │                 │
│ Methods         │ Metrics Table   │ References      │
│                 │                 │                 │
│ Figure A:       │                 │ QR Code /       │
│ Error Hist      │                 │ Repo Link       │
│                 │                 │                 │
│ Figure B:       │                 │                 │
│ Sample Path     │                 │                 │
└─────────────────┴─────────────────┴─────────────────┘
```

---

## 9. One-Minute Talk Track

1. **Hook:** "Stockouts cost money. So does over-stocking. How do we balance?"
2. **Problem:** "Classical inventory policies often use fixed or assumed demand variability."
3. **Idea:** "We calibrate σ directly from historical forecast errors using bootstrap."
4. **Method:** "Monte Carlo simulation under lost sales, lead time L=1, across volatility scenarios."
5. **Policies:** "Static (r,Q) ignores learned σ; Tuned (r,Q) uses it in safety stock."
6. **Result 1:** "Tuned policy achieves ~94% fill rate vs. ~85% for static."
7. **Result 2:** "Tuned policy is more robust—performance gap widens under high volatility."
8. **Tradeoff:** "Higher service comes at higher holding cost. Classic OM tradeoff."
9. **Takeaway:** "Data-driven calibration is simple, actionable, and improves consistency."
10. **Close:** "Especially valuable for retailers facing volatile, uncertain demand."

---

## 10. What to Emphasize / Avoid

### ✅ Emphasize

- **Robustness:** Tuned policy degrades gracefully under volatility.
- **Consistency:** Reliable fill rate across scenarios.
- **Tradeoffs:** Honest about service vs. cost tension.
- **Simplicity:** No complex ML—bootstrap + classical policy.
- **Decision support:** Actionable for practitioners.

### ❌ Avoid

- Calling any policy "optimal" or "best."
- Overstating generalizability (single SKU, lost sales only).
- Implying ML novelty—this is classical OM with calibration.
- Ignoring limitations.

---

## 11. Reproducibility Pointers

### Data & Results

| Artifact | Path |
|----------|------|
| Results CSV | `experiments/results_volatility.csv` |
| Analysis Notebook | `notebooks/results_analysis.ipynb` |
| Figures Directory | `figures/` |

### How to Regenerate

```bash
# 1. Run volatility experiment
python experiments/run_volatility_experiment.py

# 2. Open notebook for analysis and figures
jupyter notebook notebooks/results_analysis.ipynb

# 3. Figures saved to figures/
```

---

## 12. References

- [Ref 1] Classic (r, Q) inventory models and reorder point policies.
- [Ref 2] Safety stock formulations under demand uncertainty.
- [Ref 3] Bootstrap methods for uncertainty quantification.
- [Ref 4] Monte Carlo simulation in Operations Management.
- [Ref 5] Service level vs. holding cost tradeoffs in inventory control.

---

*Poster prepared for: Operations Management & Supply Chain Analytics – Amazon Project PBL*
