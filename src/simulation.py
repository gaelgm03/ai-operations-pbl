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


def policy_adapter_historical_mean(
    inventory_position: float,
    params: Dict[str, float]
) -> Tuple[bool, float]:
    """Adapter for historical-mean policy using trailing demand average.

    This adapter is used internally by run_monte_carlo_simulation when
    simulating the historical-mean policy. The trailing mean is computed
    externally and passed via params.

    Args:
        inventory_position: Current inventory position (unused for this policy).
        params: Dict with key "trailing_mean" containing the trailing average demand.

    Returns:
        Tuple (True, order_qty) where order_qty equals the trailing mean.
    """
    trailing_mean = params.get("trailing_mean", 0.0)
    return (True, trailing_mean)


def _generate_stochastic_demand(
    demand_forecast: np.ndarray,
    error_samples: np.ndarray,
    rng: np.random.Generator
) -> np.ndarray:
    """Generate a stochastic demand path via bootstrap sampling.

    Samples forecast errors with replacement and adds them to the forecast.
    Demand is floored at zero to avoid negative values.

    Args:
        demand_forecast: Array of forecast values (length T).
        error_samples: Array of historical forecast errors for bootstrap sampling.
        rng: NumPy random generator for reproducibility.

    Returns:
        Array of stochastic demand values (length T), each >= 0.
    """
    T = len(demand_forecast)
    sampled_errors = rng.choice(error_samples, size=T, replace=True)
    stochastic_demand = demand_forecast + sampled_errors
    stochastic_demand = np.maximum(0.0, stochastic_demand)
    return stochastic_demand


def run_monte_carlo_simulation(
    demand_forecast: np.ndarray,
    error_samples: np.ndarray,
    policy_decision_fn: Callable,
    policy_params: Dict[str, float],
    initial_inventory: float,
    n_runs: int,
    random_seed: Optional[int] = None
) -> List[pd.DataFrame]:
    """Run Monte Carlo simulation with multiple stochastic demand paths.

    For each run:
    1. Sample forecast errors independently for each period (bootstrap with replacement).
    2. Construct stochastic demand path: D_t = max(0, forecast_t + ε_t).
    3. Run a single simulation using run_single_simulation.
    4. Store the resulting DataFrame.

    Args:
        demand_forecast: Array of forecast values per period (length T).
        error_samples: Array of historical forecast errors for bootstrap sampling.
        policy_decision_fn: Function(inventory_position, params) -> (place_order, qty).
        policy_params: Parameters to pass to the policy function.
        initial_inventory: Starting on-hand inventory.
        n_runs: Number of Monte Carlo replications to run.
        random_seed: Optional seed for reproducibility.

    Returns:
        List of DataFrames, one per run, each containing simulation history.
    """
    rng = np.random.default_rng(random_seed)
    results: List[pd.DataFrame] = []

    for run_idx in range(n_runs):
        stochastic_demand = _generate_stochastic_demand(
            demand_forecast, error_samples, rng
        )

        df_run = run_single_simulation(
            demand_series=stochastic_demand,
            forecast_series=demand_forecast,
            policy_decision_fn=policy_decision_fn,
            policy_params=policy_params,
            initial_inventory=initial_inventory
        )

        df_run["run"] = run_idx
        results.append(df_run)

    return results


def run_monte_carlo_simulation_historical_mean(
    demand_forecast: np.ndarray,
    error_samples: np.ndarray,
    initial_inventory: float,
    n_runs: int,
    window: int = 5,
    random_seed: Optional[int] = None
) -> List[pd.DataFrame]:
    """Run Monte Carlo simulation using historical-mean policy.

    At each period, the order quantity equals the trailing mean of realized
    demand over the last `window` periods. For periods with fewer than `window`
    observations, uses all available realized demand.

    For each run:
    1. Sample forecast errors independently for each period (bootstrap with replacement).
    2. Construct stochastic demand path: D_t = max(0, forecast_t + ε_t).
    3. Simulate inventory dynamics with trailing-mean ordering.
    4. Store the resulting DataFrame.

    Args:
        demand_forecast: Array of forecast values per period (length T).
        error_samples: Array of historical forecast errors for bootstrap sampling.
        initial_inventory: Starting on-hand inventory.
        n_runs: Number of Monte Carlo replications to run.
        window: Number of periods for trailing mean calculation (default 5).
        random_seed: Optional seed for reproducibility.

    Returns:
        List of DataFrames, one per run, each containing simulation history.
    """
    rng = np.random.default_rng(random_seed)
    results: List[pd.DataFrame] = []
    T = len(demand_forecast)

    for run_idx in range(n_runs):
        stochastic_demand = _generate_stochastic_demand(
            demand_forecast, error_samples, rng
        )

        state = initialize_simulation(initial_inventory, T)
        realized_demands: List[float] = []

        for t in range(T):
            if len(realized_demands) == 0:
                trailing_mean = 0.0
            else:
                lookback = realized_demands[-window:]
                trailing_mean = float(np.mean(lookback))

            policy_params = {"trailing_mean": trailing_mean}

            state = simulate_single_period(
                state,
                demand=stochastic_demand[t],
                forecast=demand_forecast[t],
                policy_decision_fn=policy_adapter_historical_mean,
                policy_params=policy_params
            )

            realized_demands.append(stochastic_demand[t])

        df_run = pd.DataFrame(state["history"])
        df_run.index.name = "period"
        df_run["run"] = run_idx
        results.append(df_run)

    return results


def aggregate_simulation_results(
    simulation_outputs: List[pd.DataFrame]
) -> Dict[str, float]:
    """Aggregate results across simulation replications."""
    pass
