"""
Demand uncertainty modeling module.

This module handles the quantification and modeling of demand uncertainty
using statistical distributions and probabilistic methods.

Responsibilities:
- Estimate demand distribution parameters
- Fit probability distributions to demand data
- Generate demand scenarios for simulation
- Calculate uncertainty metrics
"""

from typing import Dict
import pandas as pd
import numpy as np


def compute_forecast_error_distribution(
    actuals: pd.Series,
    forecasts: pd.Series
) -> Dict[str, object]:
    """
    Compute the distribution of forecast errors.

    Forecast error is defined as: error = actual - forecast.
    Returns statistical summaries and the empirical error samples.

    Parameters
    ----------
    actuals : pd.Series
        Series of actual demand values (Units Sold).
    forecasts : pd.Series
        Series of forecasted demand values (Demand Forecast).

    Returns
    -------
    Dict[str, object]
        Dictionary containing:
        - 'mean_error': float, mean of forecast errors
        - 'std_error': float, standard deviation of forecast errors
        - 'error_samples': np.ndarray, array of individual forecast errors
    """
    errors = actuals.values - forecasts.values
    return {
        "mean_error": float(np.mean(errors)),
        "std_error": float(np.std(errors, ddof=1)),
        "error_samples": errors,
    }


def calculate_demand_variability(
    demand_data: pd.Series
) -> Dict[str, float]:
    """
    Calculate measures of demand variability.

    Computes basic statistical measures of demand to quantify
    variability for inventory planning purposes.

    Parameters
    ----------
    demand_data : pd.Series
        Series of demand values (Units Sold).

    Returns
    -------
    Dict[str, float]
        Dictionary containing:
        - 'mean_demand': float, mean of demand
        - 'std_demand': float, standard deviation of demand
    """
    return {
        "mean_demand": float(np.mean(demand_data.values)),
        "std_demand": float(np.std(demand_data.values, ddof=1)),
    }
