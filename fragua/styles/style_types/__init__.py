"""
Styles types package for Fragua.
"""

from .delivery_style_types import (
    ExcelDeliveryStyle,
    SQLDeliveryStyle,
    APIDeliveryStyle,
)
from .extraction_style_types import (
    CSVExtractionStyle,
    ExcelExtractionStyle,
    SQLExtractionStyle,
    APIExtractionStyle,
)
from .forge_style_types import (
    MLForgeStyle,
    ReportForgeStyle,
    AnalysisForgeStyle,
)


__all__ = [
    "SQLDeliveryStyle",
    "APIDeliveryStyle",
    "ExcelDeliveryStyle",
    "CSVExtractionStyle",
    "ExcelExtractionStyle",
    "SQLExtractionStyle",
    "APIExtractionStyle",
    "MLForgeStyle",
    "ReportForgeStyle",
    "AnalysisForgeStyle",
]
