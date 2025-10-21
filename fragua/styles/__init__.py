"""
Styles package for Fragua.
"""

from .delivery_style import DeliveryStyle
from .mine_style import MineStyle
from .forge_style import ForgeStyle

from .style_types.delivery_style_types import (
    SQLDeliveryStyle,
    APIDeliveryStyle,
    ExcelDeliveryStyle,
)
from .style_types.mine_style_types import (
    CSVMineStyle,
    ExcelMineStyle,
    SQLMineStyle,
    APIMineStyle,
)

from .style_types.forge_style_types import (
    MLForgeStyle,
    ReportForgeStyle,
    AnalysisForgeStyle,
)


__all__ = [
    "DeliveryStyle",
    "MineStyle",
    "ForgeStyle",
    "CSVMineStyle",
    "ExcelMineStyle",
    "SQLMineStyle",
    "APIMineStyle",
    "MLForgeStyle",
    "ReportForgeStyle",
    "AnalysisForgeStyle",
    "SQLDeliveryStyle",
    "APIDeliveryStyle",
    "ExcelDeliveryStyle",
]
