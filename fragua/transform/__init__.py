"""
Transform module.

This module contains:
- Transformer agent subclass.
- Transform Params subclasses.
- Transform Style subclasses.
- Transform FraguaFunctions subclasses.
"""

# ------------------- Extract Functions ------------------- #
from .transform_functions import (
    TRANSFORM_FUNCTION_CLASSES,
    TransformFunction,
    AnalysisTransformFunction,
    ReportTransformFunction,
    MLTransformFunction,
)

# ------------------- Extract Styles ------------------- #
from .transform_styles import (
    TRANSFORM_STYLE_CLASSES,
    TransformStyle,
    MLTransformStyle,
    ReportTransformStyle,
    AnalysisTransformStyle,
)

# ------------------- Extract Params ------------------- #


# ------------------- Transformer Agent ------------------- #
from .transformer import Transformer


__all__ = [
    # Extractor Agent
    "Transformer",
    # Extract Params
    # Extract Functions
    "TRANSFORM_FUNCTION_CLASSES",
    "TransformFunction",
    "AnalysisTransformFunction",
    "ReportTransformFunction",
    "MLTransformFunction",
    # Extract Styles
    "TRANSFORM_STYLE_CLASSES",
    "TransformStyle",
    "MLTransformStyle",
    "ReportTransformStyle",
    "AnalysisTransformStyle",
]
