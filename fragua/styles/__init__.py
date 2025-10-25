"""Fragua Styles package."""

# ------------------- Base Styles ------------------- #
from .delivery_style import DeliveryStyle
from .mine_style import MineStyle
from .forge_style import ForgeStyle

# ------------------- Delivery Style Types ------------------- #
from .style_types.delivery_style_types import (
    SQLDeliveryStyle,
    APIDeliveryStyle,
    ExcelDeliveryStyle,
)

# ------------------- Mine Style Types ------------------- #
from .style_types.mine_style_types import (
    CSVMineStyle,
    ExcelMineStyle,
    SQLMineStyle,
    APIMineStyle,
)

# ------------------- Forge Style Types ------------------- #
from .style_types.forge_style_types import (
    MLForgeStyle,
    ReportForgeStyle,
    AnalysisForgeStyle,
)

# ------------------- __all__ ------------------- #
__all__ = [
    # Base Styles
    "DeliveryStyle",
    "MineStyle",
    "ForgeStyle",
    # Mine Styles
    "CSVMineStyle",
    "ExcelMineStyle",
    "SQLMineStyle",
    "APIMineStyle",
    # Forge Styles
    "MLForgeStyle",
    "ReportForgeStyle",
    "AnalysisForgeStyle",
    # Delivery Styles
    "SQLDeliveryStyle",
    "APIDeliveryStyle",
    "ExcelDeliveryStyle",
]
