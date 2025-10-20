"""
Styles package for Fragua.
"""

from .delivery_style import DeliveryStyle
from .extraction_style import ExtractionStyle
from .forge_style import ForgeStyle

from .style_types import (
    CSVExtractionStyle,
    ExcelExtractionStyle,
    SQLExtractionStyle,
    APIExtractionStyle,
    MLForgeStyle,
    ReportForgeStyle,
    AnalysisForgeStyle,
    SQLDeliveryStyle,
    APIDeliveryStyle,
    ExcelDeliveryStyle,
)

__extraction__ = [
    "CSVExtractionStyle",
    "ExcelExtractionStyle",
    "SQLExtractionStyle",
    "APIExtractionStyle",
]

__forge__ = [
    "MLForgeStyle",
    "ReportForgeStyle",
    "AnalysisForgeStyle",
]

__delivery__ = [
    "ExcelDeliveryStyle",
    "SQLDeliveryStyle",
    "APIDeliveryStyle",
]


__all__ = [
    "DeliveryStyle",
    "ExtractionStyle",
    "ForgeStyle",
    "CSVExtractionStyle",
    "ExcelExtractionStyle",
    "SQLExtractionStyle",
    "APIExtractionStyle",
    "MLForgeStyle",
    "ReportForgeStyle",
    "AnalysisForgeStyle",
    "SQLDeliveryStyle",
    "APIDeliveryStyle",
    "ExcelDeliveryStyle",
]
