"""
Transform style types for various data transformation scenarios.
"""

from abc import abstractmethod
from typing import Any, Dict, Generic

import pandas as pd

from fragua.functions.transform_functions import (
    AnalysisTransformFunction,
    MLTransformFunction,
    ReportTransformFunction,
)
from fragua.core.style import Style, ResultT
from fragua.utils.logger import get_logger
from fragua.params.transform_params import (
    TransformParams,
    TransformParamsT,
    MLTransformParamsT,
    ReportTransformParamsT,
    AnalysisTransformParamsT,
)

logger = get_logger(__name__)


# ---------------------------------------------------------------------- #
# Base TransformStyle
# ---------------------------------------------------------------------- #
class TransformStyle(
    Style[TransformParamsT, ResultT], Generic[TransformParamsT, ResultT]
):
    """
    Base class for all transformation styles in Fragua ETL.

    Standard pipeline provided by Style:
        validate_params -> _run -> validate_result -> postprocess
    """

    @abstractmethod
    def transform(self, params: TransformParamsT) -> ResultT:
        """
        Base transform method. Should be implemented by subclasses
        to call the appropriate registered function.
        """
        raise NotImplementedError

    def _run(self, params: TransformParamsT) -> ResultT:
        logger.debug("Starting TransformStyle '%s' transformation.", self.style_name)
        result = self.transform(params)
        logger.debug("TransformStyle '%s' transformation completed.", self.style_name)
        return result


# ---------------------------------------------------------------------- #
# ML Transform
# ---------------------------------------------------------------------- #
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


# ---------------------------------------------------------------------- #
# Report Transform
# ---------------------------------------------------------------------- #
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


# ---------------------------------------------------------------------- #
# Analysis Transform
# ---------------------------------------------------------------------- #
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


TRANSFORM_STYLE_CLASSES: Dict[str, type[TransformStyle[TransformParams, Any]]] = {
    "ml": MLTransformStyle,
    "report": ReportTransformStyle,
    "analysis": AnalysisTransformStyle,
}
