"""Fragua package."""

# ------------------- Agents ------------------- #
from fragua.agents import Miner, Blacksmith, Transporter, StoreManager

# ------------------- Styles ------------------- #
from fragua.styles import (
    ForgeStyle,
    ReportForgeStyle,
    MLForgeStyle,
    AnalysisForgeStyle,
    DeliveryStyle,
    SQLDeliveryStyle,
    APIDeliveryStyle,
    ExcelDeliveryStyle,
    MineStyle,
    CSVMineStyle,
    ExcelMineStyle,
    SQLMineStyle,
    APIMineStyle,
)

# ------------------- Store ------------------- #
from fragua.store import Store, Wagon, Box, Container

# ------------------- Base Classes ------------------- #
from fragua.core import BaseAgent, BaseStyle, BaseStorage

# ------------------- Params ------------------- #
from fragua.params import (
    register_params,
    ForgeParams,
    ForgeParamsT,
    DeliveryParams,
    DeliveryParamsT,
    MineParams,
    MineParamsT,
    ExcelMineParams,
    ExcelMineParamsT,
    CSVMineParams,
    CSVMineParamsT,
    SQLMineParams,
    SQLMineParamsT,
    APIMineParams,
    APIMineParamsT,
    MLForgeParams,
    MLForgeParamsT,
    ReportForgeParams,
    ReportForgeParamsT,
    AnalysisForgeParams,
    AnalysisForgeParamsT,
    SQLDeliveryParams,
    SQLDeliveryParamsT,
    APIDeliveryParams,
    APIDeliveryParamsT,
    ExcelDeliveryParams,
    ExcelDeliveryParamsT,
)

# ------------------- Utilities ------------------- #
from fragua.utils import (
    get_logger,
    Config,
    calculate_checksum,
    get_local_time_and_offset,
    generate_metadata,
    add_metadata_to_storage,
)

# ------------------- __all__ ------------------- #
__all__ = [
    # Agents
    "Miner",
    "Blacksmith",
    "Transporter",
    "StoreManager",
    # Store
    "Store",
    "Wagon",
    "Box",
    "Container",
    # Base Classes
    "BaseAgent",
    "BaseStyle",
    "BaseStorage",
    # Styles
    "ForgeStyle",
    "ReportForgeStyle",
    "MLForgeStyle",
    "AnalysisForgeStyle",
    "DeliveryStyle",
    "SQLDeliveryStyle",
    "APIDeliveryStyle",
    "ExcelDeliveryStyle",
    "MineStyle",
    "CSVMineStyle",
    "ExcelMineStyle",
    "SQLMineStyle",
    "APIMineStyle",
    # Params
    "register_params",
    "ForgeParams",
    "ForgeParamsT",
    "DeliveryParams",
    "DeliveryParamsT",
    "MineParams",
    "MineParamsT",
    "ExcelMineParams",
    "ExcelMineParamsT",
    "CSVMineParams",
    "CSVMineParamsT",
    "SQLMineParams",
    "SQLMineParamsT",
    "APIMineParams",
    "APIMineParamsT",
    "MLForgeParams",
    "MLForgeParamsT",
    "ReportForgeParams",
    "ReportForgeParamsT",
    "AnalysisForgeParams",
    "AnalysisForgeParamsT",
    "SQLDeliveryParams",
    "SQLDeliveryParamsT",
    "APIDeliveryParams",
    "APIDeliveryParamsT",
    "ExcelDeliveryParams",
    "ExcelDeliveryParamsT",
    # Utilities
    "get_logger",
    "Config",
    "calculate_checksum",
    "get_local_time_and_offset",
    "generate_metadata",
    "add_metadata_to_storage",
]
