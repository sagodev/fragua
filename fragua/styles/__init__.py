"""
Styles package for Fragua.
"""

from .delivery_style import DeliveryStyle
from .extraction_style import ExtractionStyle
from .forge_style import ForgeStyle

from .style_types.delivery_style_types import (
    SQLDeliveryStyle,
    APIDeliveryStyle,
    ExcelDeliveryStyle,
)
from .style_types.extraction_style_types import (
    CSVExtractionStyle,
    ExcelExtractionStyle,
    SQLExtractionStyle,
    APIExtractionStyle,
)

from .style_types.forge_style_types import (
    MLForgeStyle,
    ReportForgeStyle,
    AnalysisForgeStyle,
)


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
