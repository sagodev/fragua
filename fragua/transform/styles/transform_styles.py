"""
Transform style types for various data transformation scenarios.
"""

from typing import Any, Dict, Type
import pandas as pd

from fragua.transform.functions.transform_functions import (
    AnalysisTransformFunction,
    MLTransformFunction,
    ReportTransformFunction,
)

from fragua.transform.params.base import TransformParams
from fragua.transform.params.transform_params import (
    AnalysisTransformParams,
    MLTransformParams,
    ReportTransformParams,
)

from fragua.transform.styles.base import TransformStyle


class MLTransformStyle(TransformStyle):
    """Transform style for machine learning preprocessing."""

    def transform(self, params: MLTransformParams) -> pd.DataFrame:
        return MLTransformFunction(params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        return {
            "style_name": self.__class__.__name__,
            "purpose": "Apply machine learning preprocessing steps.",
            "action": "transform",
            "parameters_type": "MLTransformParams",
            "function": "MLTransformFunction",
        }


class ReportTransformStyle(TransformStyle):
    """Transform style for reporting transformations."""

    def transform(self, params: ReportTransformParams) -> pd.DataFrame:
        return ReportTransformFunction(params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        return {
            "style_name": self.__class__.__name__,
            "purpose": "Prepare data for reporting.",
            "action": "transform",
            "parameters_type": "ReportTransformParams",
            "function": "ReportTransformFunction",
        }


class AnalysisTransformStyle(TransformStyle):
    """Transform style for data analysis transformations."""

    def transform(self, params: AnalysisTransformParams) -> pd.DataFrame:
        return AnalysisTransformFunction(params).execute()

    def summary_fields(self) -> Dict[str, Any]:
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
