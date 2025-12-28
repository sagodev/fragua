"""
Transform Functions.
"""

from typing import Callable, Dict, Iterable, Optional, Union

import pandas as pd
from fragua.transform.functions.internal_functions import (
    TRANSFORM_INTERNAL_FUNCTIONS,
)

from fragua.utils.types.enums import ActionType, FieldType, TargetType


def execute_transform_pipeline(
    input_data: pd.DataFrame,
    steps: Iterable[str],
    config_keys: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Execute a transformation pipeline composed of ordered steps.

    Args:
        input_data:
            Input DataFrame to be transformed.
        params:
            Configuration object containing transformation options.
        steps:
            Ordered list of internal transform step names.
        context:
            Optional execution context (reserved for future use).

    Returns:
        pd.DataFrame:
            Transformed DataFrame.

    Raises:
        KeyError:
            If a transformation step is not registered.
    """
    data = input_data

    for step in steps:
        if step not in TRANSFORM_INTERNAL_FUNCTIONS:
            raise KeyError(f"Transform function '{step}' not registered.")

        spec = TRANSFORM_INTERNAL_FUNCTIONS[step]

        kwargs = {
            key: getattr(config_keys, key)
            for key in spec.config_keys
            if hasattr(config_keys, key)
        }

        data = spec.func(data, config=kwargs or None)

    return data


def transform_ml(
    data: pd.DataFrame,
    config_keys: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Apply ML-ready transformations including cleanup, encoding,
    outlier treatment, and scaling.
    """
    return execute_transform_pipeline(
        input_data=data,
        config_keys=config_keys,
        steps=[
            "fill_missing",
            "standardize",
            "encode_categoricals",
            "treat_outliers",
            "scale_numeric",
        ],
    )


def transform_report(
    input_data: pd.DataFrame,
    config_keys: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Prepare data for reporting by cleaning values, standardizing text,
    adding derived columns, and formatting numbers.
    """
    return execute_transform_pipeline(
        input_data=input_data,
        config_keys=config_keys,
        steps=[
            "fill_missing",
            "standardize",
            "add_derived_columns",
            "format_numeric",
        ],
    )


def transform_analysis(
    data: pd.DataFrame,
    config_keys: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """
    Prepare datasets for exploratory analysis using grouping,
    aggregation, sorting, and basic cleanup.
    """
    return execute_transform_pipeline(
        input_data=data,
        config_keys=config_keys,
        steps=[
            "fill_missing",
            "standardize",
            "group_and_aggregate",
            "sort_dataframe",
        ],
    )


TRANSFORM_FUNCTIONS: Dict[str, Dict[str, Union[str, Callable]]] = {
    TargetType.ML.value: {
        FieldType.ACTION.value: ActionType.TRANSFORM.value,
        FieldType.PURPOSE.value: (
            "Apply ML-ready transformations including cleanup, "
            "encoding, outlier treatment, and scaling."
        ),
        FieldType.FUNCTION.value: transform_ml,
    },
    TargetType.REPORT.value: {
        FieldType.ACTION.value: ActionType.TRANSFORM.value,
        FieldType.PURPOSE.value: (
            "Prepare data for reporting by cleaning values, "
            "standardizing text, adding derived columns, "
            "and formatting numbers."
        ),
        FieldType.FUNCTION.value: transform_report,
    },
    TargetType.ANALYSIS.value: {
        FieldType.ACTION.value: ActionType.TRANSFORM.value,
        FieldType.PURPOSE.value: (
            "Prepare datasets for exploratory analysis using grouping, "
            "aggregation, sorting, and basic cleanup."
        ),
        FieldType.FUNCTION.value: transform_analysis,
    },
}
