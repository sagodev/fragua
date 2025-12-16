"""
Transform Functions.
"""

from __future__ import annotations
from typing import Any, Dict, Type

import pandas as pd
from fragua.core.function import FraguaFunction
from fragua.core.params import FraguaParamsT
from fragua.transform.functions.internal_functions import (
    TRANSFORM_INTERNAL_FUNCTIONS,
)

from fragua.transform.params.transform_params import (
    AnalysisTransformParams,
    MLTransformParams,
    ReportTransformParams,
)


class TransformPipeline(FraguaFunction[FraguaParamsT]):
    """
    Base class for transformation pipelines executed as ordered steps.
    """

    action = "transform"

    def execute(
        self,
        input_data: pd.DataFrame,
        params: FraguaParamsT,
        context: Any = None,
    ) -> pd.DataFrame:
        """
        Execute the transformation pipeline.

        Args:
            input_data: Input DataFrame to be transformed.
            params: Configuration object containing transformation options.
            context: Optional execution context (reserved for future use).

        Returns:
            pd.DataFrame: Transformed DataFrame.

        Raises:
            KeyError: If a transformation step is not registered.
        """
        data = input_data

        for step in self.steps or ():
            if step not in TRANSFORM_INTERNAL_FUNCTIONS:
                raise KeyError(f"Transform function '{step}' not registered.")

            spec = TRANSFORM_INTERNAL_FUNCTIONS[step]

            kwargs = {
                key: getattr(params, key)
                for key in spec.config_keys
                if hasattr(params, key)
            }

            data = spec.func(data, **kwargs)

        return data


class MLTransformFunction(TransformPipeline[MLTransformParams]):
    """
    Transformation designed for Machine Learning workflows.
    """

    action = "transform"
    params_type = MLTransformParams
    purpose = (
        "Apply ML-ready transformations including cleanup, "
        "encoding, outlier treatment, and scaling."
    )

    steps = [
        "fill_missing",
        "standardize",
        "encode_categoricals",
        "treat_outliers",
        "scale_numeric",
    ]


class ReportTransformFunction(TransformPipeline[ReportTransformParams]):
    """
    Transformation pipeline tailored for reporting and presentation.
    """

    action = "transform"
    params_type = ReportTransformParams
    purpose = (
        "Prepare data for reporting by cleaning values, "
        "standardizing text, adding derived columns, "
        "and formatting numbers."
    )

    steps = [
        "fill_missing",
        "standardize",
        "add_derived_columns",
        "format_numeric",
    ]


class AnalysisTransformFunction(TransformPipeline[AnalysisTransformParams]):
    """
    Transformation pipeline for exploratory and analytical workflows.
    """

    action = "transform"
    params_type = AnalysisTransformParams
    purpose = (
        "Prepare datasets for exploratory analysis using grouping, "
        "aggregation, sorting, and basic cleanup."
    )

    steps = [
        "fill_missing",
        "standardize",
        "group_and_aggregate",
        "sort_dataframe",
    ]


TRANSFORM_FUNCTION_CLASSES: Dict[str, Type[FraguaFunction]] = {
    "ml": MLTransformFunction,
    "report": ReportTransformFunction,
    "analysis": AnalysisTransformFunction,
}
