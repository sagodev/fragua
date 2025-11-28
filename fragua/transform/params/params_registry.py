"""Transform Params Registry."""

from typing import Dict
from fragua.transform.params.base import TransformParams
from fragua.transform.params.transform_params import (
    AnalysisTransformParams,
    MLTransformParams,
    ReportTransformParams,
)


TRANSFORM_PARAMS_CLASSES: Dict[str, type[TransformParams]] = {
    "ml": MLTransformParams,
    "report": ReportTransformParams,
    "analysis": AnalysisTransformParams,
}
