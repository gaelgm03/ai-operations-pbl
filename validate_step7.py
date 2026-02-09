"""
Validation script for Step 7: metrics computation and Monte Carlo aggregation.
"""

import numpy as np

from src.preprocessing import preprocess_pipeline
from src.calibration import run_calibration
from src.forecasting import generate_forecasts
from src.policies import configure_static_rq, configure_tuned_rq
from src.simulation import policy_adapter_rq, run_monte_carlo_simulation
from src.metrics import summarize_monte_carlo, summarize_run


def main():
    print("=" * 60)
    print("STEP 7 VALIDATION: Metrics & Monte Carlo Aggregation")
    print("=" * 60)

    # --- SETUP ---
    print("\n--- SETUP ---")

    # Load data and calibration
    df = preprocess_pipeline("data/retail_store_inventory.csv")
    print(f"Loaded preprocessed data: {len(df)} rows")

    calib_table, error_samples_by_group, group_col = run_calibration(
        "data/retail_store_inventory.csv"
    )
    print(f"Calibration complete: {len(calib_table)} groups")

    # Pick group with largest n_obs
    idx_max = calib_table["n_obs"].idxmax()
    group_name = calib_table.loc[idx_max, "group"]

    # Filter to group and take horizon T=120
    df_g = df[df[group_col] == group_name].sort_values("Date").iloc[:120]
    demand = df_g["Units Sold"].to_numpy()
    forecast = generate_forecasts(df_g, method="dataset").to_numpy()
    errors = error_samples_by_group[group_name]

    print(f"Filtered to {len(df_g)} periods for group '{group_name}'")

    # --- RUN SMALL MONTE CARLO ---
    print("\n--- RUN SMALL MONTE CARLO ---")

    mean_d = float(demand.mean())
    std_d = float(demand.std())
    L = 1
    Q = 200.0
    z = 1.0

    params_static = configure_static_rq(mean_d, L, Q, z)
    params_tuned = configure_tuned_rq(mean_d, std_d, L, Q, z)

    print(f"Static params: r = {params_static['reorder_point']:.2f}, Q = {params_static['order_quantity']:.2f}")
    print(f"Tuned params:  r = {params_tuned['reorder_point']:.2f}, Q = {params_tuned['order_quantity']:.2f}")

    runs_static = run_monte_carlo_simulation(
        demand_forecast=forecast,
        error_samples=errors,
        policy_decision_fn=policy_adapter_rq,
        policy_params=params_static,
        initial_inventory=300.0,
        n_runs=20,
        random_seed=7
    )

    runs_tuned = run_monte_carlo_simulation(
        demand_forecast=forecast,
        error_samples=errors,
        policy_decision_fn=policy_adapter_rq,
        policy_params=params_tuned,
        initial_inventory=300.0,
        n_runs=20,
        random_seed=7
    )

    print(f"Generated {len(runs_static)} static runs, {len(runs_tuned)} tuned runs")

    # --- METRICS VALIDATION ---
    print("\n--- METRICS VALIDATION ---")

    # Single-run summary
    one = summarize_run(runs_static[0], h=1.0)
    print("\nSingle run summary:")
    for k, v in one.items():
        print(f"  {k}: {v:.4f}")

    # Aggregated summaries
    agg_static = summarize_monte_carlo(runs_static, h=1.0)
    agg_tuned = summarize_monte_carlo(runs_tuned, h=1.0)

    print("\nSTATIC summary table:")
    print(agg_static.to_string())

    print("\nTUNED summary table:")
    print(agg_tuned.to_string())

    # --- SANITY CHECKS ---
    print("\n--- SANITY CHECKS ---")

    # Fill rate should be between 0 and 1
    fr_static = agg_static.loc["fill_rate", "mean"]
    fr_tuned = agg_tuned.loc["fill_rate", "mean"]
    check_fr_static = 0.0 <= fr_static <= 1.0
    check_fr_tuned = 0.0 <= fr_tuned <= 1.0
    print(f"Fill rate (static) in [0,1]: {check_fr_static} (value: {fr_static:.4f})")
    print(f"Fill rate (tuned) in [0,1]:  {check_fr_tuned} (value: {fr_tuned:.4f})")

    # Stockout rates should be between 0 and 1
    so_event_static = agg_static.loc["stockout_event", "mean"]
    so_event_tuned = agg_tuned.loc["stockout_event", "mean"]
    so_vol_static = agg_static.loc["stockout_volume", "mean"]
    so_vol_tuned = agg_tuned.loc["stockout_volume", "mean"]

    check_so_event = 0.0 <= so_event_static <= 1.0 and 0.0 <= so_event_tuned <= 1.0
    check_so_vol = 0.0 <= so_vol_static <= 1.0 and 0.0 <= so_vol_tuned <= 1.0
    print(f"Stockout event rates in [0,1]: {check_so_event}")
    print(f"Stockout volume rates in [0,1]: {check_so_vol}")

    # Holding cost should be >= 0
    hc_static = agg_static.loc["holding_cost", "mean"]
    hc_tuned = agg_tuned.loc["holding_cost", "mean"]
    check_hc = hc_static >= 0 and hc_tuned >= 0
    print(f"Holding cost >= 0: {check_hc} (static: {hc_static:.2f}, tuned: {hc_tuned:.2f})")

    # CI low <= mean <= CI high for each metric
    def check_ci_order(agg_df):
        all_ok = True
        for metric in agg_df.index:
            m = agg_df.loc[metric, "mean"]
            lo = agg_df.loc[metric, "ci_low"]
            hi = agg_df.loc[metric, "ci_high"]
            if not (lo <= m <= hi):
                all_ok = False
                print(f"  CI order FAIL for {metric}: {lo:.4f} <= {m:.4f} <= {hi:.4f}")
        return all_ok

    print("CI order (static): ", end="")
    ci_ok_static = check_ci_order(agg_static)
    print(ci_ok_static if ci_ok_static else "")

    print("CI order (tuned):  ", end="")
    ci_ok_tuned = check_ci_order(agg_tuned)
    print(ci_ok_tuned if ci_ok_tuned else "")

    # --- GROUP INFO ---
    print("\n--- CHOSEN GROUP INFO ---")
    print(f"group_col: {group_col}")
    print(f"group_name: {group_name}")

    row = calib_table[calib_table["group"] == group_name].iloc[0]
    print(f"n_obs: {row['n_obs']}")
    print(f"mu_demand: {row['mu_demand']:.2f}")
    print(f"sigma_demand: {row['sigma_demand']:.2f}")
    print(f"mu_error: {row['mu_error']:.2f}")
    print(f"sigma_error: {row['sigma_error']:.2f}")

    # --- SUMMARY ---
    print("\n" + "=" * 60)
    all_checks = [
        check_fr_static, check_fr_tuned,
        check_so_event, check_so_vol,
        check_hc,
        ci_ok_static, ci_ok_tuned
    ]
    if all(all_checks):
        print("ALL SANITY CHECKS PASSED")
    else:
        n_failed = sum(1 for c in all_checks if not c)
        print(f"SOME CHECKS FAILED: {n_failed}/{len(all_checks)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
