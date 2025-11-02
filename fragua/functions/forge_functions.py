"""
Reusable Forge Functions.
"""

from __future__ import annotations
from typing import Any
import numpy as np
import pandas as pd
from pandas.errors import UndefinedVariableError
from sklearn.preprocessing import MinMaxScaler

from fragua.functions.function_registry import register_function
from fragua.params.forge_params import (
    MLForgeParams,
    ReportForgeParams,
    AnalysisForgeParams,
)
from fragua.utils.logger import get_logger

logger = get_logger(__name__)

action: str = "forge"

# ----------------------------- #
# --- Data Cleaning Helpers --- #
# ----------------------------- #


@register_function(action, "fill_missing")
def fill_missing(params: Any) -> pd.DataFrame:
    """
    Fill missing values in numeric and categorical columns.

    Args:
        params (Any): Parameters containing the DataFrame and strategy attributes.

    Returns:
        pd.DataFrame: DataFrame with missing values filled.
    """
    df = params.data.copy()
    numeric_fill = getattr(params, "numeric_fill", "mean")
    categorical_fill = getattr(params, "categorical_fill", "unknown")

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            fill_value = df[col].mean() if numeric_fill == "mean" else 0
            df[col] = df[col].fillna(fill_value)
        else:
            df[col] = df[col].fillna(categorical_fill)

    params.data = df
    logger.info("forge: Missing values filled.")
    return df


@register_function(action, "standardize")
def standardize(params: Any) -> pd.DataFrame:
    """
    Standardize string columns by trimming and lowering case.

    Args:
        params (Any): Parameters containing the DataFrame.

    Returns:
        pd.DataFrame: Standardized DataFrame.
    """
    df = params.data.copy()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip().str.lower()
    params.data = df
    logger.info("forge: String columns standardized.")
    return df


@register_function(action, "encode_categoricals")
def encode_categoricals(params: Any) -> pd.DataFrame:
    """
    Encode categorical columns into dummy variables.

    Args:
        params (Any): Parameters containing the DataFrame.

    Returns:
        pd.DataFrame: DataFrame with categorical columns encoded.
    """
    df = params.data.copy()
    cat_cols = df.select_dtypes(include="object").columns
    if len(cat_cols) > 0:
        df = pd.get_dummies(df, columns=cat_cols)
        logger.info("forge: Encoded categoricals: %s", list(cat_cols))
    params.data = df
    return df


@register_function(action, "scale_numeric")
def scale_numeric(params: Any) -> pd.DataFrame:
    """
    Scale numeric columns using MinMaxScaler.

    Args:
        params (Any): Parameters containing the DataFrame.

    Returns:
        pd.DataFrame: Scaled DataFrame.
    """
    df = params.data.copy()
    num_cols = df.select_dtypes(include="number").columns
    if len(num_cols) > 0:
        scaler = MinMaxScaler()
        df[num_cols] = scaler.fit_transform(df[num_cols])
        logger.info("forge: Scaled numeric columns: %s", list(num_cols))
    params.data = df
    return df


@register_function(action, "treat_outliers")
def treat_outliers(params: Any) -> pd.DataFrame:
    """
    Cap outliers in numeric columns using the IQR method.

    Args:
        params (Any): Parameters containing the DataFrame and outlier threshold.

    Returns:
        pd.DataFrame: DataFrame with outliers treated.
    """
    df = params.data.copy()
    factor = getattr(params, "outlier_threshold", 1.5)
    num_cols = df.select_dtypes(include="number").columns

    for col in num_cols:
        Q1, Q3 = df[col].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        df[col] = np.clip(df[col], Q1 - factor * IQR, Q3 + factor * IQR)

    params.data = df
    logger.info("forge: Outliers treated with factor %.2f", factor)
    return df


@register_function(action, "add_derived_columns")
def add_derived_columns(params: Any) -> pd.DataFrame:
    """
    Add derived or computed columns to the DataFrame.

    Args:
        params (Any): Parameters containing the DataFrame and derived column definitions.

    Returns:
        pd.DataFrame: DataFrame with derived columns added.
    """
    df = params.data.copy()
    derived = getattr(params, "derived_columns", None)

    if derived:
        for new_col, expr in derived.items():
            try:
                df[new_col] = df.eval(expr)
                logger.debug(
                    "forge: Derived column '%s' created from '%s'.", new_col, expr
                )
            except (UndefinedVariableError, SyntaxError, TypeError, ValueError) as e:
                logger.warning("forge: Could not compute '%s': %s", new_col, e)
    elif {"quantity", "price"}.issubset(df.columns):
        df["total"] = df["quantity"] * df["price"]
        logger.debug("forge: Default derived column 'total' added.")

    params.data = df
    return df


# ----------------------------- #
# --- MLForge Pipeline --- #
# ----------------------------- #
@register_function("forge", "forge_ml")
def forge_ml(params: MLForgeParams) -> pd.DataFrame:
    """
    Full MLForge pipeline using registered functions:
    fill_missing, standardize, encode_categoricals, treat_outliers, scale_numeric.

    Args:
        params (MLForgeParams): Parameters including data and preprocessing options.

    Returns:
        pd.DataFrame: Transformed DataFrame for ML.
    """
    fill_missing(params)
    standardize(params)
    encode_categoricals(params)
    treat_outliers(params)
    scale_numeric(params)
    return params.data


# ----------------------------- #
# --- ReportForge Pipeline --- #
# ----------------------------- #
@register_function("forge", "forge_report")
def forge_report(params: ReportForgeParams) -> pd.DataFrame:
    """
    Full ReportForge pipeline using registered functions:
    fill_missing, standardize, add_derived_columns, and formatting.

    Args:
        params (ReportForgeParams): Parameters data, derived columns, and rounding precision.

    Returns:
        pd.DataFrame: Transformed DataFrame ready for reporting.
    """
    fill_missing(params)
    standardize(params)
    add_derived_columns(params)

    # Format numeric columns
    df = params.data
    precision = (
        2
        if getattr(params, "rounding_precision", None) is None
        else params.rounding_precision
    )
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].round(precision)
    params.data = df
    return df


# ----------------------------- #
# --- AnalysisForge Pipeline --- #
# ----------------------------- #
@register_function("forge", "forge_analysis")
def forge_analysis(params: AnalysisForgeParams) -> pd.DataFrame:
    """
    Full AnalysisForge pipeline using registered functions:
    fill_missing, standardize, group/aggregate, sort.

    Args:
        params (AnalysisForgeParams): Parameters data, groupby, aggregation, and sorting options.

    Returns:
        pd.DataFrame: Transformed DataFrame for analysis.
    """
    fill_missing(params)
    standardize(params)

    df = params.data
    groupby_cols = getattr(params, "groupby_cols", []) or []
    agg_functions = getattr(params, "agg_functions", {}) or {}
    sort_by = getattr(params, "sort_by", []) or []

    if groupby_cols:
        if agg_functions:
            df = df.groupby(groupby_cols).agg(agg_functions).reset_index()
        else:
            df = df.groupby(groupby_cols).agg("sum").reset_index()

    if sort_by:
        df = df.sort_values(by=sort_by)

    params.data = df
    return df
