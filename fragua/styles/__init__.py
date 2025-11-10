"""Fragua Styles package."""

# ------------------- Base Style ------------------- #
from .style import Style, STYLE_REGISTRY, register_style, get_style, list_styles

# ------------------- Load Style Types ------------------- #
from .load_styles import (
    LoadStyle,
    SQLLoadStyle,
    APILoadStyle,
    ExcelLoadStyle,
)

# ------------------- Extract Styles ------------------- #
from .extract_styles import (
    ExtractStyle,
    CSVExtractStyle,
    ExcelExtractStyle,
    SQLExtractStyle,
    APIExtractStyle,
)

# ------------------- Transform Styles ------------------- #
from .transform_styles import (
    TransformStyle,
    MLTransformStyle,
    ReportTransformStyle,
    AnalysisTransformStyle,
)


# ------------------- __all__ ------------------- #
__all__ = [
    # Base Styles
    "Style",
    "LoadStyle",
    "ExtractStyle",
    "TransformStyle",
    # Extract Styles
    "CSVExtractStyle",
    "ExcelExtractStyle",
    "SQLExtractStyle",
    "APIExtractStyle",
    # Transform Styles
    "MLTransformStyle",
    "ReportTransformStyle",
    "AnalysisTransformStyle",
    # Load Styles
    "SQLLoadStyle",
    "APILoadStyle",
    "ExcelLoadStyle",
    # Styles Registry Functions
    "STYLE_REGISTRY",
    "register_style",
    "get_style",
    "list_styles",
]
