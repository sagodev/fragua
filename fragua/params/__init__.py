"""Fragua ETL Params module."""

# ------------------- Params Registry ------------------- #
from .params_registry import register_params

# ------------------- Delivery Params ------------------- #
from .delivery_params import (
    DeliveryParams,
    ExcelDeliveryParams,
    SQLDeliveryParams,
    APIDeliveryParams,
    DeliveryParamsT,
    ExcelDeliveryParamsT,
    SQLDeliveryParamsT,
    APIDeliveryParamsT,
)

# ------------------- Mine Params ------------------- #
from .mine_params import (
    MineParams,
    CSVMineParams,
    ExcelMineParams,
    SQLMineParams,
    APIMineParams,
    MineParamsT,
    CSVMineParamsT,
    ExcelMineParamsT,
    SQLMineParamsT,
    APIMineParamsT,
)

# ------------------- Forge Params ------------------- #
from .forge_params import (
    ForgeParams,
    MLForgeParams,
    ReportForgeParams,
    AnalysisForgeParams,
    ForgeParamsT,
    MLForgeParamsT,
    ReportForgeParamsT,
    AnalysisForgeParamsT,
)

# ------------------- __all__ ------------------- #
__all__ = [
    # Params Registry
    "register_params",
    # Mine Params
    "MineParams",
    "CSVMineParams",
    "ExcelMineParams",
    "SQLMineParams",
    "APIMineParams",
    "MineParamsT",
    "CSVMineParamsT",
    "ExcelMineParamsT",
    "SQLMineParamsT",
    "APIMineParamsT",
    # Delivery Params
    "DeliveryParams",
    "ExcelDeliveryParams",
    "SQLDeliveryParams",
    "APIDeliveryParams",
    "DeliveryParamsT",
    "ExcelDeliveryParamsT",
    "SQLDeliveryParamsT",
    "APIDeliveryParamsT",
    # Forge Params
    "ForgeParams",
    "MLForgeParams",
    "ReportForgeParams",
    "AnalysisForgeParams",
    "ForgeParamsT",
    "MLForgeParamsT",
    "ReportForgeParamsT",
    "AnalysisForgeParamsT",
]
