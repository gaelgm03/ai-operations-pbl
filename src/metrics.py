"""
Performance metrics module.

This module calculates key performance indicators for inventory
management including service levels, costs, and efficiency metrics.

Responsibilities:
- Calculate service level metrics (fill rate, cycle service level)
- Calculate cost metrics (holding, ordering, stockout costs)
- Calculate efficiency metrics (turnover, days of supply)
- Provide summary statistics for simulation outputs
- Aggregate metrics across Monte Carlo runs with confidence intervals
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


# =============================================================================
# Per-run metric functions (from simulation DataFrame)
# =============================================================================

def stockout_rate_event(sim_df: pd.DataFrame) -> float:
    """Compute event-based stockout rate.

    Args:
        sim_df: Simulation output DataFrame with 'lost_sales' column.

    Returns:
        Fraction of periods with lost_sales > 0.
    """
    lost_sales = sim_df["lost_sales"].to_numpy()
    n_periods = len(lost_sales)
    if n_periods == 0:
        return np.nan
    n_stockout_events = np.sum(lost_sales > 0)
    return float(n_stockout_events / n_periods)


def stockout_rate_volume(sim_df: pd.DataFrame) -> float:
    """Compute volume-based stockout rate.

    Args:
        sim_df: Simulation output DataFrame with 'lost_sales' and 'demand' columns.

    Returns:
        total_lost_sales / total_demand. Returns np.nan if total_demand is zero.
    """
    total_lost_sales = sim_df["lost_sales"].sum()
    total_demand = sim_df["demand"].sum()
    if total_demand == 0:
        return np.nan
    return float(total_lost_sales / total_demand)


def fill_rate(sim_df: pd.DataFrame) -> float:
    """Compute fill rate (service level).

    Args:
        sim_df: Simulation output DataFrame with 'sales' and 'demand' columns.

    Returns:
        total_sales / total_demand. Returns np.nan if total_demand is zero.
    """
    total_sales = sim_df["sales"].sum()
    total_demand = sim_df["demand"].sum()
    if total_demand == 0:
        return np.nan
    return float(total_sales / total_demand)


def holding_cost(sim_df: pd.DataFrame, h: float = 1.0) -> float:
    """Compute total holding cost over the simulation horizon.

    Args:
        sim_df: Simulation output DataFrame with 'ending_inventory' column.
        h: Unit holding cost coefficient per period.

    Returns:
        Sum of ending_inventory * h across all periods.
    """
    total_inventory = sim_df["ending_inventory"].sum()
    return float(total_inventory * h)


def inventory_turnover(sim_df: pd.DataFrame) -> float:
    """Compute inventory turnover ratio.

    Args:
        sim_df: Simulation output DataFrame with 'sales' and 'ending_inventory' columns.

    Returns:
        total_sales / average_ending_inventory. Returns np.nan if avg inventory is zero.
    """
    total_sales = sim_df["sales"].sum()
    avg_inventory = sim_df["ending_inventory"].mean()
    if avg_inventory == 0 or np.isnan(avg_inventory):
        return np.nan
    return float(total_sales / avg_inventory)


def summarize_run(sim_df: pd.DataFrame, h: float = 1.0) -> Dict[str, float]:
    """Compute all metrics for a single simulation run.

    Args:
        sim_df: Simulation output DataFrame.
        h: Unit holding cost coefficient.

    Returns:
        Dict with keys: fill_rate, stockout_event, stockout_volume, holding_cost, turnover.
    """
    return {
        "fill_rate": fill_rate(sim_df),
        "stockout_event": stockout_rate_event(sim_df),
        "stockout_volume": stockout_rate_volume(sim_df),
        "holding_cost": holding_cost(sim_df, h),
        "turnover": inventory_turnover(sim_df),
    }


# =============================================================================
# Aggregation utilities
# =============================================================================

def aggregate_metrics(run_summaries: List[Dict[str, float]]) -> pd.DataFrame:
    """Convert list of run summary dicts to a DataFrame.

    Args:
        run_summaries: List of dicts, each from summarize_run.

    Returns:
        DataFrame with one row per run, columns = metric names.
    """
    return pd.DataFrame(run_summaries)


def mean_ci95(values: np.ndarray) -> Tuple[float, float, float]:
    """Compute mean and 95% confidence interval (normal approximation).

    Uses nanmean/nanstd to handle NaN values gracefully.

    Args:
        values: Array of metric values across runs.

    Returns:
        Tuple (mean, ci_low, ci_high) where ci = mean ± 1.96 * se.
    """
    arr = np.asarray(values, dtype=np.float64)
    n = np.sum(~np.isnan(arr))
    if n == 0:
        return (np.nan, np.nan, np.nan)
    mean_val = float(np.nanmean(arr))
    std_val = float(np.nanstd(arr, ddof=1)) if n > 1 else 0.0
    se = std_val / np.sqrt(n)
    ci_low = mean_val - 1.96 * se
    ci_high = mean_val + 1.96 * se
    return (mean_val, ci_low, ci_high)


def summarize_monte_carlo(
    sim_runs: List[pd.DataFrame],
    h: float = 1.0
) -> pd.DataFrame:
    """Aggregate metrics across Monte Carlo simulation runs.

    For each run, computes summarize_run, then aggregates to compute
    mean and 95% CI for each metric.

    Args:
        sim_runs: List of simulation output DataFrames (one per run).
        h: Unit holding cost coefficient.

    Returns:
        DataFrame with rows = metric names, columns = [mean, ci_low, ci_high].
    """
    run_summaries = [summarize_run(df, h) for df in sim_runs]
    metrics_df = aggregate_metrics(run_summaries)

    results = {}
    for col in metrics_df.columns:
        values = metrics_df[col].to_numpy()
        mean_val, ci_low, ci_high = mean_ci95(values)
        results[col] = {"mean": mean_val, "ci_low": ci_low, "ci_high": ci_high}

    summary_df = pd.DataFrame(results).T
    summary_df.index.name = "metric"
    return summary_df


# =============================================================================
# Legacy stub functions (for backward compatibility)
# =============================================================================

def calculate_fill_rate(
    demand: np.ndarray, 
    fulfilled: np.ndarray
) -> float:
    """Calculate the fill rate (fraction of demand satisfied)."""
    total_demand = np.sum(demand)
    if total_demand == 0:
        return np.nan
    return float(np.sum(fulfilled) / total_demand)


def calculate_cycle_service_level(
    stockout_cycles: int, 
    total_cycles: int
) -> float:
    """Calculate cycle service level."""
    if total_cycles == 0:
        return np.nan
    return float(1.0 - stockout_cycles / total_cycles)


def calculate_holding_cost(
    inventory_levels: np.ndarray, 
    unit_holding_cost: float
) -> float:
    """Calculate total holding cost."""
    return float(np.sum(inventory_levels) * unit_holding_cost)


def calculate_ordering_cost(
    n_orders: int, 
    fixed_ordering_cost: float
) -> float:
    """Calculate total ordering cost."""
    return float(n_orders * fixed_ordering_cost)


def calculate_stockout_cost(
    stockout_quantity: np.ndarray, 
    unit_stockout_cost: float
) -> float:
    """Calculate total stockout cost."""
    return float(np.sum(stockout_quantity) * unit_stockout_cost)


def calculate_total_cost(
    inventory_levels: np.ndarray,
    n_orders: int,
    stockout_quantity: np.ndarray,
    costs: Dict[str, float]
) -> float:
    """Calculate total inventory cost."""
    h_cost = calculate_holding_cost(inventory_levels, costs.get("holding", 0.0))
    o_cost = calculate_ordering_cost(n_orders, costs.get("ordering", 0.0))
    s_cost = calculate_stockout_cost(stockout_quantity, costs.get("stockout", 0.0))
    return h_cost + o_cost + s_cost


def calculate_inventory_turnover(
    total_demand: float, 
    average_inventory: float
) -> float:
    """Calculate inventory turnover ratio."""
    if average_inventory == 0:
        return np.nan
    return float(total_demand / average_inventory)


def calculate_days_of_supply(
    average_inventory: float, 
    average_daily_demand: float
) -> float:
    """Calculate days of supply."""
    if average_daily_demand == 0:
        return np.nan
    return float(average_inventory / average_daily_demand)


def generate_performance_summary(
    simulation_output: pd.DataFrame, 
    costs: Dict[str, float]
) -> Dict[str, float]:
    """Generate comprehensive performance summary."""
    return summarize_run(simulation_output, costs.get("holding", 1.0))
