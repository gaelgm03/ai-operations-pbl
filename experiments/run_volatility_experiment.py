"""
STEP 8: Core experiments for volatility scenarios.

Compare Static (r, Q) vs Tuned (r, Q) under three demand volatility regimes:
- Low volatility: 0.5 × σ
- Baseline volatility: 1.0 × σ
- High volatility: 1.5 × σ

Uncertainty is varied by scaling the empirical forecast-error samples.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.preprocessing import preprocess_pipeline
from src.calibration import run_calibration
from src.forecasting import generate_forecasts
from src.policies import configure_static_rq, configure_tuned_rq
from src.simulation import run_monte_carlo_simulation, policy_adapter_rq
from src.metrics import summarize_monte_carlo


def main() -> None:
    data_path = "data/retail_store_inventory.csv"

    df = preprocess_pipeline(data_path)

    calib_table, error_samples_by_group, group_col = run_calibration(data_path)

    idx_max = calib_table["n_obs"].idxmax()
    group_name = calib_table.loc[idx_max, "group"]

    df_g = df[df[group_col] == group_name].reset_index(drop=True)

    T = min(365, len(df_g))
    df_g = df_g.iloc[:T].reset_index(drop=True)

    forecast = generate_forecasts(df_g, method="dataset").to_numpy()
    demand = df_g["Units Sold"].to_numpy()
    errors = error_samples_by_group[group_name]

    L = 1
    Q = 200.0
    z = 1.0
    mean_d = demand.mean()
    std_d = demand.std()

    params_static = configure_static_rq(mean_d, L, Q, z)
    params_tuned = configure_tuned_rq(mean_d, std_d, L, Q, z)

    volatility_multipliers = [0.5, 1.0, 1.5]
    results_rows = []

    for m in volatility_multipliers:
        scaled_errors = errors * m

        runs_static = run_monte_carlo_simulation(
            demand_forecast=forecast,
            error_samples=scaled_errors,
            policy_decision_fn=policy_adapter_rq,
            policy_params=params_static,
            initial_inventory=300.0,
            n_runs=300,
            random_seed=11
        )
        table_static = summarize_monte_carlo(runs_static, h=1.0)

        runs_tuned = run_monte_carlo_simulation(
            demand_forecast=forecast,
            error_samples=scaled_errors,
            policy_decision_fn=policy_adapter_rq,
            policy_params=params_tuned,
            initial_inventory=300.0,
            n_runs=300,
            random_seed=11
        )
        table_tuned = summarize_monte_carlo(runs_tuned, h=1.0)

        for policy_name, table in [("static", table_static), ("tuned", table_tuned)]:
            row = {
                "volatility_multiplier": m,
                "policy": policy_name,
                "fill_rate_mean": table.loc["fill_rate", "mean"],
                "fill_rate_ci_low": table.loc["fill_rate", "ci_low"],
                "fill_rate_ci_high": table.loc["fill_rate", "ci_high"],
                "stockout_event_mean": table.loc["stockout_event", "mean"],
                "stockout_event_ci_low": table.loc["stockout_event", "ci_low"],
                "stockout_event_ci_high": table.loc["stockout_event", "ci_high"],
                "stockout_volume_mean": table.loc["stockout_volume", "mean"],
                "stockout_volume_ci_low": table.loc["stockout_volume", "ci_low"],
                "stockout_volume_ci_high": table.loc["stockout_volume", "ci_high"],
                "holding_cost_mean": table.loc["holding_cost", "mean"],
                "holding_cost_ci_low": table.loc["holding_cost", "ci_low"],
                "holding_cost_ci_high": table.loc["holding_cost", "ci_high"],
                "turnover_mean": table.loc["turnover", "mean"],
                "turnover_ci_low": table.loc["turnover", "ci_low"],
                "turnover_ci_high": table.loc["turnover", "ci_high"],
            }
            results_rows.append(row)

    comparison_df = pd.DataFrame(results_rows)

    print("Volatility Experiment Results")
    print("=" * 60)
    print(comparison_df.head(10))
    print(f"\nShape: {comparison_df.shape}")

    output_path = Path(__file__).resolve().parent / "results_volatility.csv"
    comparison_df.to_csv(output_path, index=False)
    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
