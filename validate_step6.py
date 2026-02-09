"""
Validation script for Step 6: Monte Carlo simulation for inventory policies.
"""

import numpy as np

from src.preprocessing import preprocess_pipeline
from src.calibration import run_calibration
from src.forecasting import generate_forecasts
from src.policies import configure_static_rq, configure_tuned_rq
from src.simulation import (
    policy_adapter_rq,
    run_monte_carlo_simulation,
    run_monte_carlo_simulation_historical_mean
)


def main():
    print("=" * 60)
    print("STEP 6 VALIDATION: Monte Carlo Simulation")
    print("=" * 60)

    # --- SETUP ---
    print("\n--- SETUP ---")

    # Load data
    df = preprocess_pipeline("data/retail_store_inventory.csv")
    print(f"Loaded preprocessed data: {len(df)} rows")

    # Run calibration
    calib_table, error_samples_by_group, group_col = run_calibration(
        "data/retail_store_inventory.csv"
    )
    print(f"Calibration complete: {len(calib_table)} groups")

    # Select group with largest n_obs
    idx_max = calib_table["n_obs"].idxmax()
    group_name = calib_table.loc[idx_max, "group"]

    print(f"\nChosen group_col: {group_col}")
    print(f"Chosen group_name: {group_name}")
    print("\nCalibration row for selected group:")
    print(calib_table[calib_table["group"] == group_name].to_string(index=False))

    # Filter to group and take small horizon
    df_g = df[df[group_col] == group_name].sort_values("Date").iloc[:60]
    demand = df_g["Units Sold"].to_numpy()
    forecast = generate_forecasts(df_g, method="dataset").to_numpy()
    errors = error_samples_by_group[group_name]

    print(f"\nFiltered to {len(df_g)} periods for group '{group_name}'")
    print(f"Error samples available: {len(errors)}")

    # --- POLICY PARAMS ---
    print("\n--- POLICY PARAMS ---")
    mean_d = float(demand.mean())
    std_d = float(demand.std())
    L = 1
    Q = 200.0
    z = 1.0

    params_static = configure_static_rq(mean_d, L, Q, z)
    params_tuned = configure_tuned_rq(mean_d, std_d, L, Q, z)

    print(f"mean_d = {mean_d:.2f}, std_d = {std_d:.2f}")
    print(f"params_static: r = {params_static['reorder_point']:.2f}, Q = {params_static['order_quantity']:.2f}")
    print(f"params_tuned:  r = {params_tuned['reorder_point']:.2f}, Q = {params_tuned['order_quantity']:.2f}")

    # --- TEST 1: MC for (r,Q) policy ---
    print("\n--- TEST 1: MC for (r,Q) policy ---")

    runs1 = run_monte_carlo_simulation(
        demand_forecast=forecast,
        error_samples=errors,
        policy_decision_fn=policy_adapter_rq,
        policy_params=params_static,
        initial_inventory=300.0,
        n_runs=5,
        random_seed=42
    )

    runs2 = run_monte_carlo_simulation(
        demand_forecast=forecast,
        error_samples=errors,
        policy_decision_fn=policy_adapter_rq,
        policy_params=params_static,
        initial_inventory=300.0,
        n_runs=5,
        random_seed=42
    )

    # Check: len(runs1) == 5 and len(runs2) == 5
    check1a = len(runs1) == 5
    check1b = len(runs2) == 5
    print(f"len(runs1) == 5: {'PASS' if check1a else 'FAIL'} (got {len(runs1)})")
    print(f"len(runs2) == 5: {'PASS' if check1b else 'FAIL'} (got {len(runs2)})")

    # Check: demand arrays match for run 0
    demand1 = runs1[0]["demand"].to_numpy()
    demand2 = runs2[0]["demand"].to_numpy()
    check1c = np.allclose(demand1, demand2)
    print(f"runs1[0]['demand'] == runs2[0]['demand'] (reproducibility): {'PASS' if check1c else 'FAIL'}")

    # --- TEST 2: MC for historical-mean policy ---
    print("\n--- TEST 2: MC for historical-mean policy ---")

    runs_h = run_monte_carlo_simulation_historical_mean(
        demand_forecast=forecast,
        error_samples=errors,
        initial_inventory=300.0,
        n_runs=3,
        window=5,
        random_seed=123
    )

    check2a = len(runs_h) == 3
    print(f"len(runs_h) == 3: {'PASS' if check2a else 'FAIL'} (got {len(runs_h)})")

    # Check each df has 60 rows
    check2b = all(len(df_run) == 60 for df_run in runs_h)
    row_counts = [len(df_run) for df_run in runs_h]
    print(f"Each df has 60 rows: {'PASS' if check2b else 'FAIL'} (row counts: {row_counts})")

    # Check order_qty is finite (no NaNs) after first few periods
    check2c = True
    for i, df_run in enumerate(runs_h):
        order_qty = df_run["order_qty"].to_numpy()
        # After period 0, order_qty should be finite
        if not np.all(np.isfinite(order_qty[1:])):
            check2c = False
            print(f"  Run {i}: NaN found in order_qty after period 0")
    print(f"order_qty finite after first periods: {'PASS' if check2c else 'FAIL'}")

    # --- INVARIANTS (spot check) ---
    print("\n--- INVARIANTS (spot check on runs1[0]) ---")

    r0 = runs1[0]

    # min ending_inventory >= 0
    min_inv = r0["ending_inventory"].min()
    check3a = min_inv >= 0
    print(f"min(ending_inventory) >= 0: {'PASS' if check3a else 'FAIL'} (min = {min_inv:.2f})")

    # min lost_sales >= 0
    min_lost = r0["lost_sales"].min()
    check3b = min_lost >= 0
    print(f"min(lost_sales) >= 0: {'PASS' if check3b else 'FAIL'} (min = {min_lost:.2f})")

    # arrivals[0] == 0
    arrivals_0 = r0["arrivals"].iloc[0]
    check3c = arrivals_0 == 0
    print(f"arrivals[0] == 0: {'PASS' if check3c else 'FAIL'} (got {arrivals_0:.2f})")

    # for t>=1: arrivals[t] == order_qty[t-1]
    arrivals = r0["arrivals"].to_numpy()
    order_qty = r0["order_qty"].to_numpy()
    check3d = np.allclose(arrivals[1:], order_qty[:-1])
    print(f"arrivals[t] == order_qty[t-1] for t>=1: {'PASS' if check3d else 'FAIL'}")

    # --- SUMMARY ---
    print("\n" + "=" * 60)
    all_checks = [
        check1a, check1b, check1c,
        check2a, check2b, check2c,
        check3a, check3b, check3c, check3d
    ]
    if all(all_checks):
        print("ALL CHECKS PASSED")
    else:
        n_failed = sum(1 for c in all_checks if not c)
        print(f"SOME CHECKS FAILED: {n_failed}/{len(all_checks)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
