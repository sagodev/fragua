"""Transform Set Module."""

from typing import Any, Callable, Dict, Iterable, List, Optional, Union

import pandas as pd
from fragua.core.set import FraguaSet
from fragua.sets.transform.internal_functions import (
    TRANSFORM_INTERNAL_FUNCTIONS,
)

from fragua.utils.types.enums import ITF, ActionType, FieldType, TargetType


# -----------------
# Load Functions
# -----------------


def execute_transform_pipeline(
    input_data: pd.DataFrame,
    steps: Iterable[Union[str, Callable[..., pd.DataFrame]]],
    config_keys: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Execute a transformation pipeline composed of ordered steps.

    Steps may be either the registered internal function name (str) or a
    callable accepting (data, *, config=None).

    The function resolves step names against the registered
    `TRANSFORM_INTERNAL_FUNCTIONS` FraguaSet exposed in the transform
    registry.

    Args:
        input_data: Input DataFrame to be transformed.
        steps: Ordered list of internal transform step names or callables.
        config_keys: Mapping of configuration values to pass to steps.

    Returns:
        pd.DataFrame: Transformed DataFrame.

    Raises:
        KeyError: If a named step is not registered.
        TypeError: If a step is neither str nor callable.
    """
    data = input_data

    for step in steps:
        # Named step: resolve through the FraguaSet
        if isinstance(step, str):
            spec = TRANSFORM_INTERNAL_FUNCTIONS.get_one(step)
            if spec is None:
                raise KeyError(f"Transform function '{step}' not registered.")

            # Build kwargs only from declared config_keys in the spec
            kwargs: Dict[str, Any] = {}
            if config_keys:
                if isinstance(config_keys, dict):
                    for key in spec.config_keys:
                        if key in config_keys:
                            kwargs[key] = config_keys[key]
                else:
                    for key in spec.config_keys:
                        if hasattr(config_keys, key):
                            kwargs[key] = getattr(config_keys, key)

            # invoke the function, try with config kwarg, fallback to plain call
            fn = spec.func
            try:
                data = fn(data, config=kwargs or None)
            except TypeError:
                data = fn(data)

        # Callable step: invoke directly passing the full config mapping
        elif callable(step):
            fn = step
            try:
                data = fn(data, config=config_keys or None)
            except TypeError:
                data = fn(data)

        else:
            raise TypeError("Each step must be a registered name (str) or a callable")

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
            ITF.FILL_MISSING.value,
            ITF.STANDARDIZE.value,
            ITF.ENCODE_CATEGORICALS.value,
            ITF.TREAT_OUTLIERS.value,
            ITF.SCALE_NUMERIC.value,
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
            ITF.FILL_MISSING.value,
            ITF.STANDARDIZE.value,
            ITF.ADD_DERIVED_COLUMNS.value,
            ITF.FORMAT_NUMERIC.value,
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
            ITF.FILL_MISSING.value,
            ITF.STANDARDIZE.value,
            ITF.GROUP_AND_AGGREGATE.value,
            ITF.SORT_DATAFRAME.value,
        ],
    )


FUNCTIONS: Dict[str, Dict[str, Union[str, Callable[..., Any], List[str]]]] = {
    TargetType.ML.value: {
        FieldType.ACTION.value: ActionType.TRANSFORM.value,
        FieldType.PURPOSE.value: (
            "Apply ML-ready transformations including cleanup, "
            "encoding, outlier treatment, and scaling."
        ),
        FieldType.FUNCTION.value: transform_ml,
        FieldType.STEPS.value: [
            ITF.FILL_MISSING.value,
            ITF.STANDARDIZE.value,
            ITF.ENCODE_CATEGORICALS.value,
            ITF.TREAT_OUTLIERS.value,
            ITF.SCALE_NUMERIC.value,
        ],
    },
    TargetType.REPORT.value: {
        FieldType.ACTION.value: ActionType.TRANSFORM.value,
        FieldType.PURPOSE.value: (
            "Prepare data for reporting by cleaning values, "
            "standardizing text, adding derived columns, "
            "and formatting numbers."
        ),
        FieldType.FUNCTION.value: transform_report,
        FieldType.STEPS.value: [
            ITF.FILL_MISSING.value,
            ITF.STANDARDIZE.value,
            ITF.ADD_DERIVED_COLUMNS.value,
            ITF.FORMAT_NUMERIC.value,
        ],
    },
    TargetType.ANALYSIS.value: {
        FieldType.ACTION.value: ActionType.TRANSFORM.value,
        FieldType.PURPOSE.value: (
            "Prepare datasets for exploratory analysis using grouping, "
            "aggregation, sorting, and basic cleanup."
        ),
        FieldType.FUNCTION.value: transform_analysis,
        FieldType.STEPS.value: [
            ITF.FILL_MISSING.value,
            ITF.STANDARDIZE.value,
            ITF.GROUP_AND_AGGREGATE.value,
            ITF.SORT_DATAFRAME.value,
        ],
    },
}

# ---------------------
# Transform Functions Set
# ---------------------

TRANSFORM_FUNCTIONS = FraguaSet(set_name="transform_functions", components=FUNCTIONS)
