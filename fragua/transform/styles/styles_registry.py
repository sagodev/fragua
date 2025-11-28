"""Transform Styles Registry."""

from typing import Any, Dict

from fragua.transform.params.base import TransformParams
from fragua.transform.styles.base import TransformStyle
from fragua.transform.styles.transform_styles import (
    AnalysisTransformStyle,
    MLTransformStyle,
    ReportTransformStyle,
)


TRANSFORM_STYLE_CLASSES: Dict[str, type[TransformStyle[TransformParams, Any]]] = {
    "ml": MLTransformStyle,
    "report": ReportTransformStyle,
    "analysis": AnalysisTransformStyle,
}
