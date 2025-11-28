"""Transform Function Registry."""

from typing import Any, Dict

from fragua.transform.functions.internal_functions import (
    add_derived_columns,
    encode_categoricals,
    fill_missing,
    format_numeric,
    group_and_aggregate,
    scale_numeric,
    sort_dataframe,
    standardize,
    treat_outliers,
)


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
    """Retrive describe of a function."""
    return TRANSFORM_INTERNAL_FUNCTIONS[func].get(
        "description", "No description available."
    )


def get_function(func: str) -> Any:
    """Retrive callable of a function."""
    return TRANSFORM_INTERNAL_FUNCTIONS[func].get("func", "Function not found.")


def get_function_name(func: str) -> str:
    """Retrive name of a function."""
    if func in TRANSFORM_INTERNAL_FUNCTIONS:
        return func

    return "Function not found."
