"""Fragua Styles package."""

# ------------------- Base Style ------------------- #
from .style import Style, STYLE_REGISTRY, register_style, get_style, list_styles

# ------------------- Delivery Style Types ------------------- #
from .delivery_styles import (
    DeliveryStyle,
    SQLDeliveryStyle,
    APIDeliveryStyle,
    ExcelDeliveryStyle,
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
    "DeliveryStyle",
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
    # Delivery Styles
    "SQLDeliveryStyle",
    "APIDeliveryStyle",
    "ExcelDeliveryStyle",
    # Styles Registry Functions
    "STYLE_REGISTRY",
    "register_style",
    "get_style",
    "list_styles",
]
