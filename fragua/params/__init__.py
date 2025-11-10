"""Fragua ETL Params module."""

# ------------------- Params ------------------- #
from .params import (
    Params,
    PARAMS_REGISTRY,
    register_params,
    get_params,
    list_params,
    create_params_class,
)

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

# ------------------- Extract Params ------------------- #
from .extract_params import (
    ExtractParams,
    CSVExtractParams,
    ExcelExtractParams,
    SQLExtractParams,
    APIExtractParams,
    ExtractParamsT,
    CSVExtractParamsT,
    ExcelExtractParamsT,
    SQLExtractParamsT,
    APIExtractParamsT,
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
    "Params",
    # Params Registry Functions
    "PARAMS_REGISTRY",
    "register_params",
    "get_params",
    "list_params",
    "create_params_class",
    # Extract Params
    "ExtractParams",
    "CSVExtractParams",
    "ExcelExtractParams",
    "SQLExtractParams",
    "APIExtractParams",
    "ExtractParamsT",
    "CSVExtractParamsT",
    "ExcelExtractParamsT",
    "SQLExtractParamsT",
    "APIExtractParamsT",
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
