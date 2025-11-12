"""Fragua Styles package."""

# ------------------- Base Style ------------------- #
from .style import Style


# ------------------- Extract Styles ------------------- #
from .extract_styles import (
    EXTRACT_STYLE_CLASSES,
    ExtractStyle,
    CSVExtractStyle,
    ExcelExtractStyle,
    SQLExtractStyle,
    APIExtractStyle,
)

# ------------------- Transform Styles ------------------- #
from .transform_styles import (
    TRANSFORM_STYLE_CLASSES,
    TransformStyle,
    MLTransformStyle,
    ReportTransformStyle,
    AnalysisTransformStyle,
)

# ------------------- Load Style Types ------------------- #
from .load_styles import (
    LOAD_STYLE_CLASSES,
    LoadStyle,
    ExcelLoadStyle,
)


# ------------------- __all__ ------------------- #
__all__ = [
    # Base Styles
    "Style",
    "LoadStyle",
    "ExtractStyle",
    "TransformStyle",
    # Extract Styles
    "EXTRACT_STYLE_CLASSES",
    "CSVExtractStyle",
    "ExcelExtractStyle",
    "SQLExtractStyle",
    "APIExtractStyle",
    # Transform Styles
    "TRANSFORM_STYLE_CLASSES",
    "MLTransformStyle",
    "ReportTransformStyle",
    "AnalysisTransformStyle",
    # Load Styles
    "LOAD_STYLE_CLASSES",
    "ExcelLoadStyle",
]
