"""
Transform style implementations for different data transformation scenarios.

Each TransformStyle defines how a specific category of transformations
(machine learning, reporting, or analysis) is executed by delegating
the operation to the appropriate TransformFunction and parameter type.
"""

from typing import Any, Dict, Type
import pandas as pd

from fragua.transform.functions.transform_functions import (
    AnalysisTransformFunction,
    MLTransformFunction,
    ReportTransformFunction,
)

from fragua.transform.params.base import TransformParams
from fragua.transform.params.generic_types import (
    AnalysisTransformParamsT,
    MLTransformParamsT,
    ReportTransformParamsT,
)
from fragua.transform.params.transform_params import (
    AnalysisTransformParams,
    MLTransformParams,
    ReportTransformParams,
)

from fragua.transform.styles.base import TransformStyle


class MLTransformStyle(TransformStyle[MLTransformParamsT]):
    """
    Transform style dedicated to machine learning preprocessing workflows.

    This style applies transformations typically required before
    model training or inference, such as feature engineering,
    scaling, encoding, or dataset preparation.
    """

    def transform(self, params: MLTransformParams) -> pd.DataFrame:
        """
        Execute machine learning–oriented transformations.

        Args:
            params (MLTransformParams):
                Parameters defining the preprocessing configuration
                and input dataset.

        Returns:
            pandas.DataFrame:
                Transformed dataset ready for machine learning usage.
        """
        return MLTransformFunction(params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        """
        Return metadata describing this transform style.

        Returns:
            Dict[str, Any]:
                Dictionary containing descriptive information
                about the style, its purpose, and associated
                parameters and function.
        """
        return {
            "style_name": self.__class__.__name__,
            "purpose": "Apply machine learning preprocessing steps.",
            "action": "transform",
            "parameters_type": "MLTransformParams",
            "function": "MLTransformFunction",
        }


class ReportTransformStyle(TransformStyle[ReportTransformParamsT]):
    """
    Transform style focused on preparing data for reporting outputs.

    This style applies transformations that aggregate, format,
    or restructure data to make it suitable for dashboards,
    exports, or business reports.
    """

    def transform(self, params: ReportTransformParams) -> pd.DataFrame:
        """
        Execute reporting-oriented transformations.

        Args:
            params (ReportTransformParams):
                Parameters defining report-specific transformation
                rules and input data.

        Returns:
            pandas.DataFrame:
                Dataset formatted and structured for reporting.
        """
        return ReportTransformFunction(params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        """
        Return metadata describing this transform style.

        Returns:
            Dict[str, Any]:
                Dictionary containing descriptive information
                about the style and its reporting purpose.
        """
        return {
            "style_name": self.__class__.__name__,
            "purpose": "Prepare data for reporting.",
            "action": "transform",
            "parameters_type": "ReportTransformParams",
            "function": "ReportTransformFunction",
        }


class AnalysisTransformStyle(TransformStyle[AnalysisTransformParamsT]):
    """
    Transform style for analytical data transformations.

    This style supports exploratory and analytical workflows,
    enabling transformations such as filtering, enrichment,
    and calculation of analytical metrics.
    """

    def transform(self, params: AnalysisTransformParams) -> pd.DataFrame:
        """
        Execute analysis-oriented transformations.

        Args:
            params (AnalysisTransformParams):
                Parameters defining analytical transformation logic
                and input dataset.

        Returns:
            pandas.DataFrame:
                Dataset transformed for analytical purposes.
        """
        return AnalysisTransformFunction(params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        """
        Return metadata describing this transform style.

        Returns:
            Dict[str, Any]:
                Dictionary containing descriptive information
                about the analytical transformation style.
        """
        return {
            "style_name": self.__class__.__name__,
            "purpose": "Perform analytical transformations.",
            "action": "transform",
            "parameters_type": "AnalysisTransformParams",
            "function": "AnalysisTransformFunction",
        }


TRANSFORM_STYLE_CLASSES: Dict[str, Type[TransformStyle[TransformParams]]] = {
    "ml": MLTransformStyle,
    "report": ReportTransformStyle,
    "analysis": AnalysisTransformStyle,
}
