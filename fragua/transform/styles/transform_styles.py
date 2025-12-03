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
from fragua.transform.params.generic_types import (
    AnalysisTransformParamsT,
    MLTransformParamsT,
    ReportTransformParamsT,
)

from fragua.transform.styles.base import TransformStyle


class MLTransformStyle(TransformStyle[MLTransformParamsT, pd.DataFrame]):
    """Transform style for machine learning preprocessing."""

    def transform(self, params: MLTransformParamsT) -> pd.DataFrame:
        return MLTransformFunction("transform_ml", params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        return {
            "style_name": "ml",
            "purpose": "Apply machine learning preprocessing steps.",
            "action": "transform",
            "parameters_type": "MLTransformParams",
            "pipeline": ["MLTransformFunction"],
        }


class ReportTransformStyle(TransformStyle[ReportTransformParamsT, pd.DataFrame]):
    """Transform style for reporting transformations."""

    def transform(self, params: ReportTransformParamsT) -> pd.DataFrame:
        return ReportTransformFunction("transform_report", params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        return {
            "style_name": "report",
            "purpose": "Prepare data for reporting.",
            "action": "transform",
            "parameters_type": "ReportTransformParams",
            "pipeline": ["ReportTransformFunction"],
        }


class AnalysisTransformStyle(TransformStyle[AnalysisTransformParamsT, pd.DataFrame]):
    """Transform style for data analysis transformations."""

    def transform(self, params: AnalysisTransformParamsT) -> pd.DataFrame:
        return AnalysisTransformFunction("transform_analysis", params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        return {
            "style_name": "analysis",
            "purpose": "Perform analytical transformations.",
            "action": "transform",
            "parameters_type": "AnalysisTransformParams",
            "pipeline": ["AnalysisTransformFunction"],
        }


TRANSFORM_STYLE_CLASSES: Dict[str, Type[TransformStyle[TransformParams, Any]]] = {
    "ml": MLTransformStyle,
    "report": ReportTransformStyle,
    "analysis": AnalysisTransformStyle,
}
