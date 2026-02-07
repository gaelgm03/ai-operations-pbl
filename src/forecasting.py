"""
Forecasting module for demand prediction.

This module implements simple, interpretable demand forecasts that serve
as inputs to uncertainty-aware inventory policies.

Forecast accuracy is not the goal. Robustness and clarity are.
"""

import pandas as pd
import numpy as np


def moving_average_forecast(series: pd.Series, window: int = 7) -> np.ndarray:
    """
    Compute rolling mean forecast using past data only.

    For each period t, the forecast is the mean of the previous `window`
    observations. The first `window` periods contain NaN values since
    insufficient history exists.

    Parameters
    ----------
    series : pd.Series
        Historical demand observations.
    window : int, optional
        Number of past periods to average (default is 7).

    Returns
    -------
    np.ndarray
        Array of forecasts with NaN for the first `window` periods.
    """
    forecast = series.shift(1).rolling(window=window, min_periods=window).mean()
    return forecast.to_numpy()


def exponential_smoothing_forecast(series: pd.Series, alpha: float = 0.3) -> np.ndarray:
    """
    Compute simple exponential smoothing forecast.

    The forecast for period t is a weighted average of the previous
    observation and the previous forecast:
        F_t = alpha * Y_{t-1} + (1 - alpha) * F_{t-1}

    The first forecast is initialized to the first observation.

    Parameters
    ----------
    series : pd.Series
        Historical demand observations.
    alpha : float, optional
        Smoothing parameter between 0 and 1 (default is 0.3).

    Returns
    -------
    np.ndarray
        Array of forecasts. First value is NaN (no prior data).
    """
    values = series.to_numpy()
    n = len(values)
    forecast = np.empty(n)
    forecast[0] = np.nan

    if n > 1:
        forecast[1] = values[0]
        for t in range(2, n):
            forecast[t] = alpha * values[t - 1] + (1 - alpha) * forecast[t - 1]

    return forecast


def generate_forecasts(df: pd.DataFrame, method: str = "dataset") -> pd.Series:
    """
    Generate demand forecasts using the specified method.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame with columns including 'Units Sold' and
        optionally 'Demand Forecast'.
    method : str, optional
        Forecasting method to use (default is "dataset"):
        - "dataset": Use the 'Demand Forecast' column from the data.
        - "moving_average": Use 7-period rolling mean.
        - "exp_smoothing": Use simple exponential smoothing (alpha=0.3).

    Returns
    -------
    pd.Series
        Forecast values aligned with the DataFrame index.

    Raises
    ------
    ValueError
        If an unknown method is specified.
    """
    if method == "dataset":
        return df["Demand Forecast"].copy()
    elif method == "moving_average":
        forecast_values = moving_average_forecast(df["Units Sold"])
        return pd.Series(forecast_values, index=df.index, name="Forecast")
    elif method == "exp_smoothing":
        forecast_values = exponential_smoothing_forecast(df["Units Sold"])
        return pd.Series(forecast_values, index=df.index, name="Forecast")
    else:
        raise ValueError(f"Unknown forecast method: {method}")
