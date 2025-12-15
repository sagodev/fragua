"""
Internal transformation functions used by TransformFunction pipelines.

Each function operates over a TransformParams instance, mutating
its internal DataFrame and returning the same params object to
allow sequential pipeline execution.
"""

from typing import Any, Dict
import numpy as np
import pandas as pd
from pandas.errors import UndefinedVariableError
from sklearn.preprocessing import MinMaxScaler
from fragua.transform.params.generic_types import TransformParamsT

from fragua.utils.logger import get_logger

logger = get_logger(__name__)


def fill_missing(params: TransformParamsT) -> TransformParamsT:
    """
    Fill missing values in numeric and categorical columns.

    Numeric columns are filled using the strategy defined in
    `params.numeric_fill` (default: mean). Categorical columns
    are filled using `params.categorical_fill` (default: "unknown").

    Args:
        params (TransformParamsT):
            Transformation parameters containing the input DataFrame
            and optional fill strategies.

    Returns:
        TransformParamsT:
            Parameters object with missing values resolved.
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
    logger.info("Transform: Missing values filled.")
    return params


def standardize(params: TransformParamsT) -> TransformParamsT:
    """
    Standardize string columns for consistency.

    Applies trimming and lowercase normalization to all object-type
    columns to ensure uniform textual representation.

    Args:
        params (TransformParamsT):
            Transformation parameters containing the input DataFrame.

    Returns:
        TransformParamsT:
            Parameters object with standardized string columns.
    """

    df = params.data.copy()
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip().str.lower()
    params.data = df
    logger.info("Transform: String columns standardized.")
    return params


def encode_categoricals(params: TransformParamsT) -> TransformParamsT:
    """
    Encode categorical columns into dummy variables.

    All object-type columns are converted using one-hot encoding.
    Columns are expanded using pandas.get_dummies.

    Args:
        params (TransformParamsT):
            Transformation parameters containing the input DataFrame.

    Returns:
        TransformParamsT:
            Parameters object with encoded categorical features.
    """

    df = params.data.copy()
    cat_cols = df.select_dtypes(include="object").columns
    if len(cat_cols) > 0:
        df = pd.get_dummies(df, columns=cat_cols)
        logger.info("Transform: Encoded categoricals: %s", list(cat_cols))
    params.data = df
    return params


def scale_numeric(params: TransformParamsT) -> TransformParamsT:
    """
    Scale numeric columns to a normalized range.

    Applies Min-Max scaling to all numeric columns, transforming
    values to the [0, 1] range.

    Args:
        params (TransformParamsT):
            Transformation parameters containing the input DataFrame.

    Returns:
        TransformParamsT:
            Parameters object with scaled numeric columns.
    """

    df = params.data.copy()
    num_cols = df.select_dtypes(include="number").columns
    if len(num_cols) > 0:
        scaler = MinMaxScaler()
        df[num_cols] = scaler.fit_transform(df[num_cols])
        logger.info("Transform: Scaled numeric columns: %s", list(num_cols))
    params.data = df
    return params


def treat_outliers(params: TransformParamsT) -> TransformParamsT:
    """
    Cap outliers in numeric columns using the IQR method.

    Values outside the interquartile range are clipped based on
    the factor defined in `params.outlier_threshold` (default: 1.5).

    Args:
        params (TransformParamsT):
            Transformation parameters containing the input DataFrame
            and optional outlier threshold.

    Returns:
        TransformParamsT:
            Parameters object with capped numeric outliers.
    """

    df = params.data.copy()
    factor = getattr(params, "outlier_threshold", 1.5) or 1.5
    num_cols = df.select_dtypes(include="number").columns

    for col in num_cols:
        Q1, Q3 = df[col].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        df[col] = np.clip(df[col], Q1 - factor * IQR, Q3 + factor * IQR)

    params.data = df
    logger.info("Transform: Outliers treated with factor %.2f", factor)
    return params


def add_derived_columns(params: TransformParamsT) -> TransformParamsT:
    """
    Add derived or computed columns to the DataFrame.

    Derived columns may be defined through expressions in
    `params.derived_columns`. If no definitions are provided and
    both `quantity` and `price` columns exist, a default `total`
    column is computed.

    Args:
        params (TransformParamsT):
            Transformation parameters containing the input DataFrame
            and optional derived column expressions.

    Returns:
        TransformParamsT:
            Parameters object with derived columns added.
    """

    df = params.data.copy()
    derived = getattr(params, "derived_columns", None)

    if derived:
        for new_col, expr in derived.items():
            try:
                df[new_col] = df.eval(expr)
                logger.debug(
                    "Transform: Derived column '%s' created from '%s'.", new_col, expr
                )
            except (UndefinedVariableError, SyntaxError, TypeError, ValueError) as e:
                logger.warning("Transform: Could not compute '%s': %s", new_col, e)
    elif {"quantity", "price"}.issubset(df.columns):
        df["total"] = df["quantity"] * df["price"]
        logger.debug("Transform: Default derived column 'total' added.")

    params.data = df
    return params


def format_numeric(params: TransformParamsT) -> TransformParamsT:
    """
    Format numeric columns by rounding values.

    Numeric columns are rounded according to the precision defined
    in `params.rounding_precision` (default: 2).

    Args:
        params (TransformParamsT):
            Transformation parameters containing the input DataFrame
            and rounding precision.

    Returns:
        TransformParamsT:
            Parameters object with formatted numeric values.
    """

    df = params.data.copy()
    precision = getattr(params, "rounding_precision", 2) or 2
    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].round(precision)

    params.data = df
    logger.info("Transform: Numeric columns formatted with precision %d", precision)
    return params


def group_and_aggregate(params: TransformParamsT) -> TransformParamsT:
    """
    Group and aggregate data based on provided configuration.

    Groups the DataFrame using `params.groupby_cols` and applies
    aggregation functions defined in `params.agg_functions`.
    If no aggregation functions are provided, a default sum
    aggregation is applied.

    Args:
        params (TransformParamsT):
            Transformation parameters containing grouping and
            aggregation definitions.

    Returns:
        TransformParamsT:
            Parameters object with grouped and aggregated data.
    """

    df = params.data.copy()
    groupby_cols = getattr(params, "groupby_cols", []) or []
    agg_functions = getattr(params, "agg_functions", {}) or {}

    if groupby_cols:
        if agg_functions:
            df = df.groupby(groupby_cols).agg(agg_functions).reset_index()
            logger.info(
                "Transform: Grouped by %s with custom aggregations.", groupby_cols
            )
        else:
            df = df.groupby(groupby_cols).agg("sum").reset_index()
            logger.info(
                "Transform: Grouped by %s using default sum aggregation.", groupby_cols
            )

    params.data = df
    return params


def sort_dataframe(params: TransformParamsT) -> TransformParamsT:
    """
    Sort the DataFrame by specified columns.

    Sorting is applied using the columns defined in
    `params.sort_by`, preserving default ascending order.

    Args:
        params (TransformParamsT):
            Transformation parameters containing sorting configuration.

    Returns:
        TransformParamsT:
            Parameters object with sorted data.
    """

    df = params.data.copy()
    sort_by = getattr(params, "sort_by", []) or []

    if sort_by:
        df = df.sort_values(by=sort_by)
        logger.info("Transform: Sorted DataFrame by %s.", sort_by)

    params.data = df
    return params


TRANSFORM_INTERNAL_FUNCTIONS: Dict[str, dict[str, Any]] = {
    "fill_missing": {
        "func": fill_missing,
        "description": "Fill missing values in numeric and categorical columns.",
    },
    "standardize": {
        "func": standardize,
        "description": "Trim and lowercase all string columns.",
    },
    "encode_categoricals": {
        "func": encode_categoricals,
        "description": "Convert categorical columns to dummy variables.",
    },
    "scale_numeric": {
        "func": scale_numeric,
        "description": "Scale numeric columns using MinMaxScaler.",
    },
    "treat_outliers": {
        "func": treat_outliers,
        "description": "Cap outliers using IQR method.",
    },
    "add_derived_columns": {
        "func": add_derived_columns,
        "description": "Create derived columns based on expressions.",
    },
    "format_numeric": {
        "func": format_numeric,
        "description": "Round numeric columns to a given precision.",
    },
    "group_and_aggregate": {
        "func": group_and_aggregate,
        "description": "Group and aggregate data using columns and agg functions.",
    },
    "sort_dataframe": {
        "func": sort_dataframe,
        "description": "Sort the DataFrame by specified columns.",
    },
}


def get_function_description(func: str) -> Any:
    """
    Retrieve the human-readable description of a transform function.

    Args:
        func (str): Name of the registered transform function.

    Returns:
        Any: Description text if available, otherwise a fallback message.
    """

    return TRANSFORM_INTERNAL_FUNCTIONS[func].get(
        "description", "No description available."
    )


def get_function(func: str) -> Any:
    """
    Retrieve the callable associated with a registered transform function.

    Args:
        func (str): Name of the registered transform function.

    Returns:
        Any: Callable function if found, otherwise a fallback value.
    """

    return TRANSFORM_INTERNAL_FUNCTIONS[func].get("func", "Function not found.")


def get_function_name(func: str) -> str:
    """
    Resolve and validate the name of a registered transform function.

    Args:
        func (str): Function identifier.

    Returns:
        str: Validated function name or fallback message.
    """

    if func in TRANSFORM_INTERNAL_FUNCTIONS:
        return func

    return "Function not found."
