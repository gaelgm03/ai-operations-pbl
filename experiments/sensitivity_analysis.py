"""
Sensitivity analysis experiments runner.

This script performs sensitivity analysis on key parameters including
lead time variability, demand volatility, service level targets, and
cost ratios to understand their impact on optimal policy selection.
"""

import sys
sys.path.insert(0, '..')

from src.preprocessing import preprocess_pipeline
from src.demand_uncertainty import estimate_demand_distribution
from src.policies import optimize_policy_parameters, calculate_safety_stock
from src.simulation import run_monte_carlo_simulation, aggregate_simulation_results
from src.metrics import calculate_total_cost, generate_performance_summary


def main() -> None:
    """Run sensitivity analysis experiments."""
    pass


if __name__ == "__main__":
    main()
