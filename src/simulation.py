"""
Inventory simulation module.

This module provides discrete-event simulation capabilities for
evaluating inventory policies under demand uncertainty.

Responsibilities:
- Simulate inventory dynamics over time
- Track orders, deliveries, and stockouts
- Support multiple policy types in simulation
- Generate simulation output for analysis
"""

from typing import Dict, List, Tuple, Callable, Optional
import numpy as np
import pandas as pd

from src.policies import continuous_review_policy


def initialize_simulation(
    initial_inventory: float,
    simulation_length: int
) -> Dict[str, object]:
    """Initialize simulation state.

    Args:
        initial_inventory: Starting on-hand inventory.
        simulation_length: Number of periods to simulate.

    Returns:
        State dictionary containing:
        - t: current period index (starts at 0)
        - on_order: quantity arriving next period (L=1)
        - inventory: current on-hand inventory
        - history: dict of lists for per-period tracking
    """
    state = {
        "t": 0,
        "on_order": 0.0,
        "inventory": initial_inventory,
        "history": {
            "demand": [],
            "forecast": [],
            "sales": [],
            "lost_sales": [],
            "ending_inventory": [],
            "order_qty": [],
            "arrivals": []
        }
    }
    return state


def simulate_single_period(
    state: Dict[str, object],
    demand: float,
    forecast: float,
    policy_decision_fn: Callable[[float, Dict[str, float]], Tuple[bool, float]],
    policy_params: Dict[str, float]
) -> Dict[str, object]:
    """Simulate a single period of inventory operations.

    Period logic (L=1, lost sales):
    1. Receive arrivals from previous order
    2. Observe demand and fulfill (sales = min(available, demand))
    3. Compute lost sales
    4. Make ordering decision based on ending inventory

    Args:
        state: Current simulation state dictionary.
        demand: Realized demand for this period.
        forecast: Forecast value for this period.
        policy_decision_fn: Function(inventory_position, params) -> (place_order, qty).
        policy_params: Parameters to pass to the policy function.

    Returns:
        Updated state dictionary.
    """
    arrivals_t = state["on_order"]
    inventory_start = state["inventory"] + arrivals_t
    sales_t = min(inventory_start, demand)
    lost_sales_t = demand - sales_t
    inventory_end = inventory_start - sales_t

    inventory_position = inventory_end
    place_order, order_qty = policy_decision_fn(inventory_position, policy_params)

    state["history"]["demand"].append(demand)
    state["history"]["forecast"].append(forecast)
    state["history"]["sales"].append(sales_t)
    state["history"]["lost_sales"].append(lost_sales_t)
    state["history"]["ending_inventory"].append(inventory_end)
    state["history"]["order_qty"].append(order_qty)
    state["history"]["arrivals"].append(arrivals_t)

    state["on_order"] = order_qty
    state["inventory"] = inventory_end
    state["t"] += 1

    return state


def run_single_simulation(
    demand_series: np.ndarray,
    forecast_series: np.ndarray,
    policy_decision_fn: Callable[[float, Dict[str, float]], Tuple[bool, float]],
    policy_params: Dict[str, float],
    initial_inventory: float
) -> pd.DataFrame:
    """Run a single simulation over a demand path.

    Args:
        demand_series: Array of realized demands per period.
        forecast_series: Array of forecasts per period.
        policy_decision_fn: Function(inventory_position, params) -> (place_order, qty).
        policy_params: Parameters to pass to the policy function.
        initial_inventory: Starting on-hand inventory.

    Returns:
        DataFrame with one row per period containing simulation history.
    """
    simulation_length = len(demand_series)
    state = initialize_simulation(initial_inventory, simulation_length)

    for t in range(simulation_length):
        state = simulate_single_period(
            state,
            demand=demand_series[t],
            forecast=forecast_series[t],
            policy_decision_fn=policy_decision_fn,
            policy_params=policy_params
        )

    df = pd.DataFrame(state["history"])
    df.index.name = "period"
    return df


def policy_adapter_rq(
    inventory_position: float,
    params: Dict[str, float]
) -> Tuple[bool, float]:
    """Adapter for (r, Q) continuous review policy.

    Args:
        inventory_position: Current inventory position.
        params: Dict with keys "reorder_point" and "order_quantity".

    Returns:
        Tuple (place_order, order_qty) from continuous_review_policy.
    """
    reorder_point = params["reorder_point"]
    order_quantity = params["order_quantity"]
    return continuous_review_policy(inventory_position, reorder_point, order_quantity)


def run_simulation(
    demand_scenarios: np.ndarray,
    policy_func: Callable,
    policy_params: Dict[str, float],
    initial_inventory: float,
    lead_time: int
) -> pd.DataFrame:
    """Run complete inventory simulation."""
    pass


def run_monte_carlo_simulation(
    n_replications: int,
    demand_distribution: object,
    policy_func: Callable,
    policy_params: Dict[str, float],
    simulation_length: int,
    initial_inventory: float,
    lead_time: int
) -> List[pd.DataFrame]:
    """Run Monte Carlo simulation with multiple replications."""
    pass


def aggregate_simulation_results(
    simulation_outputs: List[pd.DataFrame]
) -> Dict[str, float]:
    """Aggregate results across simulation replications."""
    pass
