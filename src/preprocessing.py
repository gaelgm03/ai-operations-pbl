"""
Preprocessing module for inventory demand data.

This module handles data loading, cleaning, and transformation tasks
required to prepare raw retail inventory data for downstream analysis
and modeling.

Responsibilities:
- Load raw CSV data
- Handle missing values and outliers
- Normalize and transform features
- Split data into training and testing sets
"""

import pandas as pd


def load_data(filepath: str) -> pd.DataFrame:
    """
    Load raw inventory data from CSV file.

    Parameters
    ----------
    filepath : str
        Path to the CSV file containing inventory data.

    Returns
    -------
    pd.DataFrame
        Raw DataFrame loaded from the CSV file.
    """
    return pd.read_csv(filepath)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values and remove invalid demand entries.

    Drops rows where 'Units Sold' or 'Demand Forecast' are missing.
    Removes rows with negative 'Units Sold' or 'Demand Forecast' values.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame with potential missing or invalid values.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with valid demand data only.
    """
    df = df.dropna(subset=["Units Sold", "Demand Forecast"])
    df = df[(df["Units Sold"] >= 0) & (df["Demand Forecast"] >= 0)]
    return df.reset_index(drop=True)


def transform_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select relevant columns and sort data by time.

    Retains columns necessary for demand uncertainty analysis:
    Date, Store ID, Product ID, Category, Units Sold, Demand Forecast.
    Ensures data is sorted chronologically by Date.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame.

    Returns
    -------
    pd.DataFrame
        Transformed DataFrame with selected columns, sorted by Date.
    """
    relevant_columns = [
        "Date",
        "Store ID",
        "Product ID",
        "Category",
        "Units Sold",
        "Demand Forecast",
    ]
    df = df[relevant_columns].copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(by="Date").reset_index(drop=True)
    return df


def preprocess_pipeline(filepath: str) -> pd.DataFrame:
    """
    Run the complete preprocessing pipeline.

    Executes load -> clean -> transform steps, then filters
    deterministically to a single store (first store alphabetically)
    to produce a clean dataset for downstream analysis.

    Parameters
    ----------
    filepath : str
        Path to the CSV file containing inventory data.

    Returns
    -------
    pd.DataFrame
        Cleaned and filtered DataFrame for one store.
    """
    df = load_data(filepath)
    df = clean_data(df)
    df = transform_features(df)
    
    # Filter deterministically to one store (first store alphabetically)
    stores = sorted(df["Store ID"].unique())
    selected_store = stores[0]
    df = df[df["Store ID"] == selected_store].reset_index(drop=True)
    
    return df
