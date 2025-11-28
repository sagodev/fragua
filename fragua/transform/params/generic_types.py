"""Generic Types for Transform Params Classes."""

from typing import TypeVar

from fragua.transform.params.base import TransformParams
from fragua.transform.params.transform_params import (
    AnalysisTransformParams,
    MLTransformParams,
    ReportTransformParams,
)


TransformParamsT = TypeVar("TransformParamsT", bound=TransformParams)
MLTransformParamsT = TypeVar("MLTransformParamsT", bound=MLTransformParams)
ReportTransformParamsT = TypeVar("ReportTransformParamsT", bound=ReportTransformParams)
AnalysisTransformParamsT = TypeVar(
    "AnalysisTransformParamsT", bound=AnalysisTransformParams
)
