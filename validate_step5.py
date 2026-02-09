"""Validation script for Step 5 policy configuration functions."""

import numpy as np
from src.policies import (
    configure_static_rq,
    configure_tuned_rq,
    historical_mean_policy
)

print("=" * 60)
print("STEP 5 VALIDATION: Policy Configuration Functions")
print("=" * 60)

# ----------------------------------------------------------------------
# Test 1: configure_static_rq
# ----------------------------------------------------------------------
print("\n--- Test 1: configure_static_rq ---")
print("Inputs: mean_demand=100.0, lead_time=2, order_quantity=500.0, z=1.65")

params_static = configure_static_rq(
    mean_demand=100.0,
    lead_time=2,
    order_quantity=500.0,
    z=1.65
)

print(f"Result: {params_static}")
print("\nExpected:")
print("  sigma == 0.0")
print("  reorder_point == 200.0  (100.0 * 2)")
print("  order_quantity == 500.0")

# ----------------------------------------------------------------------
# Test 2: configure_tuned_rq
# ----------------------------------------------------------------------
print("\n--- Test 2: configure_tuned_rq ---")
print("Inputs: mean_demand=100.0, demand_std=10.0, lead_time=4, order_quantity=500.0, z=1.65")

params_tuned = configure_tuned_rq(
    mean_demand=100.0,
    demand_std=10.0,
    lead_time=4,
    order_quantity=500.0,
    z=1.65
)

print(f"Result: {params_tuned}")
print("\nExpected:")
print("  sigma == 10.0")
print("  reorder_point == 433.0  (100*4 + 1.65*10*sqrt(4) = 400 + 33)")
print("  order_quantity == 500.0")

# ----------------------------------------------------------------------
# Test 3: historical_mean_policy
# ----------------------------------------------------------------------
print("\n--- Test 3: historical_mean_policy ---")
print("Input: trailing_mean_demand=120.0")

decision = historical_mean_policy(120.0)

print(f"Result: {decision}")
print("\nExpected:")
print("  decision == (True, 120.0)")

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)
