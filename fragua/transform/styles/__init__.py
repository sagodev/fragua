"""
Transform Styles Module.

This module contains:
- TransformStyle base class.
- Transform  ML, Analysis, Report Style class.
- Dict registry with each Style class.('name': class)
"""

from .base import TransformStyle

from .transform_styles import (
    MLTransformStyle,
    ReportTransformStyle,
    AnalysisTransformStyle,
    TRANSFORM_STYLE_CLASSES,
)

__all__ = [
    "TransformStyle",
    "MLTransformStyle",
    "ReportTransformStyle",
    "AnalysisTransformStyle",
    "TRANSFORM_STYLE_CLASSES",
]
