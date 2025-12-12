"""
Transform Functions.
"""

from __future__ import annotations
from typing import Any, Dict, Optional

import pandas as pd

from fragua.transform.functions.base import TransformFunction
from fragua.transform.functions.function_registry import (
    TRANSFORM_INTERNAL_FUNCTIONS,
    get_function_description,
    get_function_name,
)

from fragua.transform.params.transform_params import (
    AnalysisTransformParams,
    MLTransformParams,
    ReportTransformParams,
)


class MLTransformFunction(TransformFunction):
    """
    TransformFunction for ML pipelines.
    """

    PURPOSE = (
        "Apply ML-ready transformations including "
        "cleanup, encoding, outlier treatment, and scaling."
    )

    STEPS = [
        "fill_missing",
        "standardize",
        "encode_categoricals",
        "treat_outliers",
        "scale_numeric",
    ]

    def __init__(self, params: Optional[MLTransformParams] = None) -> None:
        super().__init__()
        self.params = MLTransformParams() if params is None else params

    def execute(self) -> pd.DataFrame:
        for step in self.STEPS:
            if step not in TRANSFORM_INTERNAL_FUNCTIONS:
                raise KeyError(f"Transform function '{step}' not registered.")

            func = TRANSFORM_INTERNAL_FUNCTIONS[step]["func"]
            self.params = func(self.params)

        return self.params.data

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "params_type": type(self.params).__name__,
            "purpose": self.PURPOSE,
            "steps": [
                {
                    "function": get_function_name(func),
                    "description": get_function_description(func),
                }
                for func in self.STEPS
            ],
        }


class ReportTransformFunction(TransformFunction):
    """
    TransformFunction for Report pipelines.
    """

    PURPOSE = (
        "Prepare data for reporting by cleaning values,"
        " standardizing text, adding derived columns, and formatting numbers."
    )

    STEPS = [
        "fill_missing",
        "standardize",
        "add_derived_columns",
        "format_numeric",
    ]

    def __init__(self, params: Optional[ReportTransformParams] = None) -> None:
        super().__init__()
        self.params = ReportTransformParams() if params is None else params

    def execute(self) -> pd.DataFrame:
        for step in self.STEPS:
            if step not in TRANSFORM_INTERNAL_FUNCTIONS:
                raise KeyError(f"Transform function '{step}' not registered.")

            func = TRANSFORM_INTERNAL_FUNCTIONS[step]["func"]
            self.params = func(self.params)

        return self.params.data

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "params_type": type(self.params).__name__,
            "purpose": self.PURPOSE,
            "steps": [
                {
                    "function": get_function_name(func),
                    "description": get_function_description(func),
                }
                for func in self.STEPS
            ],
        }


class AnalysisTransformFunction(TransformFunction):
    """
    TransformFunction for Analysis pipelines.
    """

    PURPOSE = (
        "Prepare datasets for exploratory analysis"
        " using grouping, aggregation, sorting, and basic cleanup."
    )

    STEPS = [
        "fill_missing",
        "standardize",
        "group_and_aggregate",
        "sort_dataframe",
    ]

    def __init__(self, params: Optional[AnalysisTransformParams] = None) -> None:
        super().__init__()
        self.params = AnalysisTransformParams() if params is None else params

    def execute(self) -> pd.DataFrame:
        for step in self.STEPS:
            if step not in TRANSFORM_INTERNAL_FUNCTIONS:
                raise KeyError(f"Transform function '{step}' not registered.")

            func = TRANSFORM_INTERNAL_FUNCTIONS[step]["func"]
            self.params = func(self.params)

        return self.params.data

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "params_type": type(self.params).__name__,
            "purpose": self.PURPOSE,
            "steps": [
                {
                    "function": get_function_name(func),
                    "description": get_function_description(func),
                }
                for func in self.STEPS
            ],
        }


TRANSFORM_FUNCTION_CLASSES: Dict[str, type[TransformFunction]] = {
    "ml": MLTransformFunction,
    "report": ReportTransformFunction,
    "analysis": AnalysisTransformFunction,
}
