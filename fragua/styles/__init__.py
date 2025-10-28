"""Fragua Styles package."""

# ------------------- Delivery Style Types ------------------- #
from .delivery_styles import (
    DeliveryStyle,
    SQLDeliveryStyle,
    APIDeliveryStyle,
    ExcelDeliveryStyle,
)

# ------------------- Mine Style Types ------------------- #
from .mine_styles import (
    MineStyle,
    CSVMineStyle,
    ExcelMineStyle,
    SQLMineStyle,
    APIMineStyle,
)

# ------------------- Forge Style Types ------------------- #
from .forge_styles import (
    ForgeStyle,
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
