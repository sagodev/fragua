"""Fragua package."""

# ------------------- Agents ------------------- #
from fragua.agents import StoreManager

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
from fragua.core import (
    Agent,
    Style,
    BaseStorage,
    Params,
    register_params,
    get_style,
    list_styles,
    register_style,
)


# ------------------- Params ------------------- #
from fragua.params import (
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
    "StoreManager",
    # Store
    "Store",
    "Wagon",
    "Box",
    "Container",
    # Base Classes
    "Agent",
    "Style",
    "Params",
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
    # Registers
    "register_params",
    "register_style",
    "get_style",
    "list_styles",
    # Utilities
    "get_logger",
    "Config",
    "calculate_checksum",
    "get_local_time_and_offset",
    "generate_metadata",
    "add_metadata_to_storage",
]
