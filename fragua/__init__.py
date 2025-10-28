"""Fragua package."""

# ------------------- Agent ------------------- #
from fragua.agent import Agent, StoreManager

# ------------------- Style ------------------- #
from fragua.style import (
    Style,
    # Forge Styles
    ForgeStyle,
    ReportForgeStyle,
    MLForgeStyle,
    AnalysisForgeStyle,
    # Delivery Styles
    DeliveryStyle,
    SQLDeliveryStyle,
    APIDeliveryStyle,
    ExcelDeliveryStyle,
    # Mine Styles
    MineStyle,
    CSVMineStyle,
    ExcelMineStyle,
    SQLMineStyle,
    APIMineStyle,
    # Styles Registry Functions
    register_style,
    get_style,
    list_styles,
)

# ------------------- Store ------------------- #
from fragua.store import Wagon, Box, Container

# ------------------- Core ------------------- #
from fragua.core import (
    Storage,
    Store,
    register_storage,
    get_storage,
    list_storages,
)


# ------------------- Params ------------------- #
from fragua.params import (
    Params,
    # Params Registry Functions
    register_params,
    # Mine Params
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
    # Forge Params
    ForgeParams,
    ForgeParamsT,
    MLForgeParams,
    MLForgeParamsT,
    ReportForgeParams,
    ReportForgeParamsT,
    AnalysisForgeParams,
    AnalysisForgeParamsT,
    # Delivery Params
    DeliveryParams,
    DeliveryParamsT,
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
    "Storage",
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
    # Params Registery Functions
    "register_params",
    # Storage Registery Functions
    "register_storage",
    "get_storage",
    "list_storages",
    # Style Registery Functions
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
