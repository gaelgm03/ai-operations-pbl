"""Validation script for Step 3: Classical (r, Q) inventory policy."""

import math
from src.policies import (
    calculate_safety_stock,
    calculate_reorder_point,
    continuous_review_policy,
)

print("=" * 60)
print("Step 3 Validation: Classical (r, Q) Inventory Policy")
print("=" * 60)

# 1. Safety Stock Calculation
print("\n1. Safety Stock Calculation")
print("-" * 40)
demand_std = 10.0
lead_time = 4
z = 1.65

ss = calculate_safety_stock(demand_std, lead_time, z)
expected_ss = z * demand_std * math.sqrt(lead_time)

print(f"   demand_std = {demand_std}")
print(f"   lead_time = {lead_time}")
print(f"   z = {z}")
print(f"   Computed SS = {ss:.4f}")
print(f"   Expected SS = {expected_ss:.4f}")
print(f"   Match: {math.isclose(ss, expected_ss)}")

# 2. Reorder Point Calculation
print("\n2. Reorder Point Calculation")
print("-" * 40)
mean_demand = 100.0
lead_time = 2
safety_stock = 30.0

r = calculate_reorder_point(mean_demand, lead_time, safety_stock)
expected_r = mean_demand * lead_time + safety_stock

print(f"   mean_demand = {mean_demand}")
print(f"   lead_time = {lead_time}")
print(f"   safety_stock = {safety_stock}")
print(f"   Computed r = {r:.4f}")
print(f"   Expected r = {expected_r:.4f}")
print(f"   Match: {math.isclose(r, expected_r)}")

# 3. Continuous Review Policy Logic
print("\n3. Continuous Review Policy Logic")
print("-" * 40)
reorder_point = 250
order_quantity = 500

# Case A: inventory_position = 260 (above reorder point)
inv_a = 260
place_order_a, order_qty_a = continuous_review_policy(inv_a, reorder_point, order_quantity)
print(f"   Case A: inventory_position = {inv_a}")
print(f"      place_order = {place_order_a} (expected: False)")
print(f"      order_qty = {order_qty_a} (expected: 0)")

# Case B: inventory_position = 250 (at reorder point)
inv_b = 250
place_order_b, order_qty_b = continuous_review_policy(inv_b, reorder_point, order_quantity)
print(f"   Case B: inventory_position = {inv_b}")
print(f"      place_order = {place_order_b} (expected: True)")
print(f"      order_qty = {order_qty_b} (expected: 500)")

# Case C: inventory_position = 200 (below reorder point)
inv_c = 200
place_order_c, order_qty_c = continuous_review_policy(inv_c, reorder_point, order_quantity)
print(f"   Case C: inventory_position = {inv_c}")
print(f"      place_order = {place_order_c} (expected: True)")
print(f"      order_qty = {order_qty_c} (expected: 500)")

print("\n" + "=" * 60)
print("Validation complete.")
print("=" * 60)
