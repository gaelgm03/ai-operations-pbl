"""
Per-category calibration module for inventory uncertainty analysis.

This module computes demand and forecast-error statistics by product category
(or SKU) to support multi-product simulation and tuned (r, Q) policies.

Responsibilities:
- Detect appropriate grouping column (category or SKU)
- Compute per-group demand and forecast error statistics
- Store empirical error samples for simulation
"""

from typing import Dict, Tuple
import pandas as pd
import numpy as np

from src.preprocessing import preprocess_pipeline


CATEGORY_CANDIDATES = ["Category", "Product Category", "ProductCategory", "category"]
SKU_CANDIDATES = ["SKU", "Product ID", "ProductID", "Item", "item"]
MIN_OBS_THRESHOLD = 10


def infer_group_column(df: pd.DataFrame) -> str:
    """
    Detect the appropriate grouping column from the DataFrame.

    Prefers category-like columns over SKU-like columns.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing inventory data.

    Returns
    -------
    str
        Name of the detected grouping column.

    Raises
    ------
    ValueError
        If no suitable grouping column is found.
    """
    columns = df.columns.tolist()

    for candidate in CATEGORY_CANDIDATES:
        if candidate in columns:
            return candidate

    for candidate in SKU_CANDIDATES:
        if candidate in columns:
            return candidate

    raise ValueError(
        f"No suitable grouping column found. "
        f"Expected one of {CATEGORY_CANDIDATES + SKU_CANDIDATES}. "
        f"Available columns: {columns}"
    )


def calibrate_by_group(
    df: pd.DataFrame,
    group_col: str
) -> Tuple[pd.DataFrame, Dict[str, np.ndarray]]:
    """
    Compute calibration statistics for each group.

    For each group, computes demand and forecast error statistics.
    Groups with fewer than MIN_OBS_THRESHOLD observations are dropped.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing 'Units Sold' and 'Demand Forecast' columns.
    group_col : str
        Name of the column to group by.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, np.ndarray]]
        - calibration_table: DataFrame with columns:
            group, n_obs, mu_demand, sigma_demand, mu_error, sigma_error
        - error_samples_by_group: dict mapping group -> np.ndarray of errors
    """
    df = df.copy()
    df["error"] = df["Units Sold"] - df["Demand Forecast"]

    groups = df[group_col].unique()
    total_groups = len(groups)
    dropped_count = 0

    calibration_rows = []
    error_samples_by_group: Dict[str, np.ndarray] = {}

    for group in groups:
        group_df = df[df[group_col] == group]
        n_obs = len(group_df)

        if n_obs < MIN_OBS_THRESHOLD:
            dropped_count += 1
            continue

        demand = group_df["Units Sold"].values
        error = group_df["error"].values

        mu_demand = float(np.mean(demand))
        sigma_demand = float(np.std(demand, ddof=1))
        mu_error = float(np.mean(error))
        sigma_error = float(np.std(error, ddof=1))

        if np.isnan(sigma_demand):
            sigma_demand = 0.0
        if np.isnan(sigma_error):
            sigma_error = 0.0

        group_str = str(group)
        calibration_rows.append({
            "group": group_str,
            "n_obs": n_obs,
            "mu_demand": mu_demand,
            "sigma_demand": sigma_demand,
            "mu_error": mu_error,
            "sigma_error": sigma_error,
        })
        error_samples_by_group[group_str] = error.astype(np.float64)

    if dropped_count > 0:
        print(
            f"Calibration: dropped {dropped_count}/{total_groups} groups "
            f"with fewer than {MIN_OBS_THRESHOLD} observations."
        )

    calibration_table = pd.DataFrame(calibration_rows)

    return calibration_table, error_samples_by_group


def run_calibration(
    filepath: str
) -> Tuple[pd.DataFrame, Dict[str, np.ndarray], str]:
    """
    Run the complete calibration pipeline.

    Loads and preprocesses data, infers the grouping column,
    and computes per-group calibration statistics.

    Parameters
    ----------
    filepath : str
        Path to the CSV file containing inventory data.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, np.ndarray], str]
        - calibration_table: DataFrame with per-group statistics
        - error_samples_by_group: dict mapping group -> error samples
        - group_col: name of the grouping column used
    """
    df = preprocess_pipeline(filepath)
    group_col = infer_group_column(df)
    calibration_table, error_samples_by_group = calibrate_by_group(df, group_col)

    return calibration_table, error_samples_by_group, group_col
