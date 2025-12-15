"""
Transform Functions.
"""

from __future__ import annotations
from typing import Any, Dict, Optional

import pandas as pd

from fragua.transform.functions.base import TransformFunction
from fragua.transform.functions.internal_functions import (
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
    Transformation pipeline designed for Machine Learning workflows.

    This function applies a predefined sequence of data preparation
    steps to produce ML-ready datasets, including normalization,
    encoding, and outlier handling.
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
        """
        Initialize the ML transformation pipeline.

        Args:
            params (Optional[MLTransformParams]):
                Parameters controlling the ML transformation process.
                If not provided, default parameters are instantiated.
        """
        super().__init__()
        self.params = MLTransformParams() if params is None else params

    def execute(self) -> pd.DataFrame:
        """
        Execute the ML transformation pipeline.

        Each step defined in `STEPS` is resolved from the internal
        transformation registry and applied sequentially to the
        parameters object.

        Returns:
            pd.DataFrame: Transformed dataset ready for ML consumption.

        Raises:
            KeyError: If a required internal transformation is not registered.
        """
        for step in self.STEPS:
            if step not in TRANSFORM_INTERNAL_FUNCTIONS:
                raise KeyError(f"Transform function '{step}' not registered.")

            func = TRANSFORM_INTERNAL_FUNCTIONS[step]["func"]
            self.params = func(self.params)

        return self.params.data

    def summary(self) -> dict[str, Any]:
        """
        Return a structured summary of the ML transformation pipeline.

        Includes the transformation purpose, parameter type, and
        an ordered list of transformation steps with descriptions.
        """
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
    Transformation pipeline tailored for reporting and presentation.

    This function prepares datasets for reporting use cases by
    standardizing values, formatting outputs, and enriching data
    with derived columns.
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
        """
        Initialize the report transformation pipeline.

        Args:
            params (Optional[ReportTransformParams]):
                Parameters controlling the report transformation logic.
        """
        super().__init__()
        self.params = ReportTransformParams() if params is None else params

    def execute(self) -> pd.DataFrame:
        """
        Execute the reporting transformation pipeline.

        Applies each registered transformation step sequentially
        to prepare the dataset for reporting or dashboarding.

        Returns:
            pd.DataFrame: Reporting-ready dataset.
        """
        for step in self.STEPS:
            if step not in TRANSFORM_INTERNAL_FUNCTIONS:
                raise KeyError(f"Transform function '{step}' not registered.")

            func = TRANSFORM_INTERNAL_FUNCTIONS[step]["func"]
            self.params = func(self.params)

        return self.params.data

    def summary(self) -> dict[str, Any]:
        """
        Return a structured summary of the report transformation pipeline.
        """
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
    Transformation pipeline for exploratory and analytical workflows.

    Focused on preparing datasets for analysis through aggregation,
    grouping, sorting, and general cleanup operations.
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
        """
        Initialize the analysis transformation pipeline.

        Args:
            params (Optional[AnalysisTransformParams]):
                Parameters controlling analytical transformations.
        """
        super().__init__()
        self.params = AnalysisTransformParams() if params is None else params

    def execute(self) -> pd.DataFrame:
        """
        Execute the analysis transformation pipeline.

        Returns:
            pd.DataFrame: Dataset prepared for exploratory analysis.
        """
        for step in self.STEPS:
            if step not in TRANSFORM_INTERNAL_FUNCTIONS:
                raise KeyError(f"Transform function '{step}' not registered.")

            func = TRANSFORM_INTERNAL_FUNCTIONS[step]["func"]
            self.params = func(self.params)

        return self.params.data

    def summary(self) -> dict[str, Any]:
        """
        Return a structured summary of the analysis transformation pipeline.
        """
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
