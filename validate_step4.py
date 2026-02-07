"""
Validation script for Step 4: Single-run inventory simulation (L=1, lost sales).
"""

import numpy as np

from src.preprocessing import preprocess_pipeline
from src.forecasting import generate_forecasts
from src.policies import calculate_safety_stock, calculate_reorder_point
from src.simulation import run_single_simulation, policy_adapter_rq


def main():
    # --- SETUP ---
    print("=" * 60)
    print("Step 4 Validation: Single-Run Inventory Simulation")
    print("=" * 60)

    # Load cleaned data
    df = preprocess_pipeline("data/retail_store_inventory.csv")

    # Create demand and forecast series for first 30 rows
    demand = df["Units Sold"].iloc[:30].to_numpy()
    forecast = generate_forecasts(df.iloc[:30], method="dataset").to_numpy()

    print(f"\nSimulation length: {len(demand)} periods")
    print(f"Demand range: [{demand.min():.2f}, {demand.max():.2f}]")
    print(f"Forecast range: [{forecast.min():.2f}, {forecast.max():.2f}]")

    # --- POLICY PARAMS ---
    mean_demand = demand.mean()
    demand_std = demand.std()
    lead_time = 1
    z = 1.0
    ss = calculate_safety_stock(demand_std, lead_time, z)
    r = calculate_reorder_point(mean_demand, lead_time, ss)
    Q = 200.0

    params = {"reorder_point": float(r), "order_quantity": float(Q)}

    print(f"\nPolicy parameters:")
    print(f"  mean_demand = {mean_demand:.2f}")
    print(f"  demand_std = {demand_std:.2f}")
    print(f"  safety_stock = {ss:.2f}")
    print(f"  reorder_point (r) = {r:.2f}")
    print(f"  order_quantity (Q) = {Q:.2f}")

    # --- RUN SIMULATION ---
    initial_inventory = 300.0
    print(f"\nInitial inventory: {initial_inventory:.2f}")

    out = run_single_simulation(
        demand_series=demand,
        forecast_series=forecast,
        policy_decision_fn=policy_adapter_rq,
        policy_params=params,
        initial_inventory=initial_inventory
    )

    # --- VALIDATIONS ---
    print("\n" + "=" * 60)
    print("Simulation Output")
    print("=" * 60)

    print("\nFirst 5 periods:")
    print(out.head())

    print("\nLast 5 periods:")
    print(out.tail())

    # Invariant checks
    print("\n" + "=" * 60)
    print("Invariant Checks")
    print("=" * 60)

    # Check 1: ending_inventory >= 0
    inv_nonneg = (out["ending_inventory"] >= 0).all()
    print(f"\n[CHECK] ending_inventory >= 0 for all periods: {'PASS' if inv_nonneg else 'FAIL'}")
    if not inv_nonneg:
        print(f"  Min ending_inventory: {out['ending_inventory'].min()}")

    # Check 2: lost_sales >= 0
    ls_nonneg = (out["lost_sales"] >= 0).all()
    print(f"[CHECK] lost_sales >= 0 for all periods: {'PASS' if ls_nonneg else 'FAIL'}")
    if not ls_nonneg:
        print(f"  Min lost_sales: {out['lost_sales'].min()}")

    # Check 3: sales <= demand
    sales_leq_demand = (out["sales"] <= out["demand"] + 1e-9).all()
    print(f"[CHECK] sales <= demand for all periods: {'PASS' if sales_leq_demand else 'FAIL'}")

    # Check 4: sales <= inventory_start
    # Compute inventory_start for each period
    inventory_start = np.zeros(len(out))
    inventory_start[0] = initial_inventory + out["arrivals"].iloc[0]
    for t in range(1, len(out)):
        inventory_start[t] = out["ending_inventory"].iloc[t - 1] + out["arrivals"].iloc[t]

    sales_leq_inv_start = (out["sales"].values <= inventory_start + 1e-9).all()
    print(f"[CHECK] sales <= inventory_start for all periods: {'PASS' if sales_leq_inv_start else 'FAIL'}")

    # --- LEAD TIME CORRECTNESS ---
    print("\n" + "=" * 60)
    print("Lead Time Checks (L=1)")
    print("=" * 60)

    # Check: arrivals[0] == 0.0
    arrivals_0_check = abs(out["arrivals"].iloc[0] - 0.0) < 1e-9
    print(f"\n[CHECK] arrivals[0] == 0.0: {'PASS' if arrivals_0_check else 'FAIL'}")
    print(f"  arrivals[0] = {out['arrivals'].iloc[0]}")

    # Check: arrivals[t] == order_qty[t-1] for t >= 1
    lead_time_correct = True
    for t in range(1, len(out)):
        expected = out["order_qty"].iloc[t - 1]
        actual = out["arrivals"].iloc[t]
        if abs(actual - expected) > 1e-9:
            lead_time_correct = False
            print(f"  MISMATCH at t={t}: arrivals={actual}, order_qty[t-1]={expected}")

    print(f"[CHECK] arrivals[t] == order_qty[t-1] for t >= 1: {'PASS' if lead_time_correct else 'FAIL'}")

    # --- SUMMARY TOTALS ---
    print("\n" + "=" * 60)
    print("Summary Totals")
    print("=" * 60)

    total_demand = out["demand"].sum()
    total_sales = out["sales"].sum()
    total_lost_sales = out["lost_sales"].sum()

    print(f"\nTotal demand: {total_demand:.2f}")
    print(f"Total sales: {total_sales:.2f}")
    print(f"Total lost sales: {total_lost_sales:.2f}")

    # Check: total_sales + total_lost_sales == total_demand
    balance_check = abs((total_sales + total_lost_sales) - total_demand) < 1e-6
    print(f"\n[CHECK] total_sales + total_lost_sales == total_demand: {'PASS' if balance_check else 'FAIL'}")
    print(f"  Difference: {abs((total_sales + total_lost_sales) - total_demand):.9f}")

    # Final summary
    print("\n" + "=" * 60)
    all_pass = (
        inv_nonneg and ls_nonneg and sales_leq_demand and sales_leq_inv_start
        and arrivals_0_check and lead_time_correct and balance_check
    )
    if all_pass:
        print("ALL CHECKS PASSED")
    else:
        print("SOME CHECKS FAILED")
    print("=" * 60)


if __name__ == "__main__":
    main()
