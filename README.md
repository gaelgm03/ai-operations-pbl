# Inventory Replenishment under Demand Uncertainty

**Operations Management & Supply Chain Analytics – Amazon Project (PBL)**

---

## 1. Project Overview

- **Decision problem:** When and how much to reorder inventory under stochastic demand.
- **Uncertainty focus:** Demand volatility calibrated from historical forecast residuals.
- **Evaluation approach:** Monte Carlo simulation with lost sales, lead time L = 1.
- **Policy comparison:** Static (r, Q) vs. Tuned (r, Q) with learned σ in safety stock.
- **Metrics:** Fill rate, stockout event rate, holding cost (mean ± 95% CI).

**Out of scope:** Pricing, network design, multi-echelon, reinforcement learning.

---

## 2. Research Question

> Does calibrating safety stock from historical forecast errors improve service level consistently across demand volatility scenarios, and what is the associated cost tradeoff?

---

## 3. Methodology (High-Level)

1. **Data preprocessing & calibration** – Extract forecast residuals from retail dataset.
2. **Forecasting layer** – Simple baseline (rolling mean); forecasting is not the focus.
3. **Demand uncertainty modeling** – Bootstrap residuals to generate stochastic demand.
4. **Inventory policies** – Static (r, Q) and Tuned (r, Q) with SS = z × σ × √L.
5. **Monte Carlo simulation** – Evaluate policies over many demand paths (n ≥ 500).
6. **Metrics & confidence intervals** – Fill rate, stockout rate, holding cost with 95% CI.
7. **Volatility stress testing** – Scenarios at σ × {0.5, 1.0, 1.5}.

---

## 4. Key Results (Summary Only)

- Tuned (r, Q) achieves **~94–95% fill rate** vs. ~85% for static policy.
- Tuned policy **reduces stockout event rate** across all volatility levels.
- Tuned policy incurs **higher holding cost**—the classic service vs. cost tradeoff.
- Performance gap **widens under high volatility**; tuned policy is more robust.
- Results are consistent across Monte Carlo replications with non-overlapping CIs.

> For a full narrative, figures, and poster-ready explanation, see [`BLOG_POSTER.md`](BLOG_POSTER.md).

---

## 5. Repository Structure

```
├── data/                   # Raw retail dataset (retail_store_inventory.csv)
├── src/                    # Core modeling modules
│   ├── calibration.py      # Uncertainty estimation from residuals
│   ├── demand_uncertainty.py
│   ├── forecasting.py
│   ├── metrics.py
│   ├── policies.py
│   ├── simulation.py
│   └── utils.py
├── experiments/            # Experiment scripts and result CSVs
│   ├── run_baselines.py
│   ├── run_tuned_policy.py
│   ├── run_volatility_experiment.py
│   └── results_volatility.csv
├── notebooks/              # Analysis and visualization
│   └── results_analysis.ipynb
├── figures/                # Generated plots (exported from notebook)
├── BLOG_POSTER.md          # Poster narrative and figure placeholders
└── README.md               # This file
```

---

## 6. How to Reproduce Results

### Environment

- Python 3.9+
- Libraries: `numpy`, `pandas`, `scipy`, `matplotlib`, `jupyter`

### Commands

```bash
# Run volatility stress-test experiment
python experiments/run_volatility_experiment.py

# Open notebook for analysis and figure generation
jupyter notebook notebooks/results_analysis.ipynb
```

Results are saved to `experiments/results_volatility.csv`.  
Figures are exported to `figures/`.

---

## 7. Collaboration Guidelines

- **New experiments:** Add scripts to `experiments/` with descriptive names.
- **Core logic:** Modify only files in `src/`. Keep functions modular.
- **Do NOT** add experiment logic directly to notebooks—notebooks are for analysis only.
- **Naming:** Use snake_case for files and functions.
- **Results:** Save CSVs to `experiments/` with timestamp or version suffix if needed.
- **Figures:** Export to `figures/` with descriptive filenames (e.g., `figure_c_fill_rate.png`).

---

## 8. Modeling Assumptions & Scope

- **Lost sales:** Unmet demand is lost (no backorders).
- **Lead time:** Fixed at L = 1 period.
- **Policies:** Classical (r, Q) only; no adaptive or learning-based policies.
- **No reinforcement learning.**
- **No pricing, promotions, or substitution effects.**
- **No multi-store or network-level decisions.**
- **Safety factor z:** Fixed and exogenous; not optimized.

---

## 9. Limitations & Extensions

### Limitations

- Residuals assumed stationary over simulation horizon.
- Single SKU / aggregated category; no multi-product interactions.
- Fixed z limits exploration of service-level optimization.
- Lead time fixed at L = 1; longer lead times not tested.

### Future Extensions (not in scope)

- Mis-specified σ robustness check.
- Non-Gaussian residuals (heavy tails).
- Lead time sensitivity (L > 1).
- Joint (z, Q) optimization.

---

## 10. References

- Classical (r, Q) inventory models and reorder point policies.
- Safety stock formulations under demand uncertainty.
- Bootstrap methods for uncertainty quantification.
- Monte Carlo simulation in Operations Management.

*No specific citations provided; references are generic and indicative.*
