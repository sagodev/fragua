"""Fragua ETL Params module."""

# ------------------- Params ------------------- #
from .params import (
    Params,
)


# ------------------- Extract Params ------------------- #
from .extract_params import (
    EXTRACT_PARAMS_CLASSES,
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

# ------------------- Transform Params ------------------- #
from .transform_params import (
    TRANSFORM_PARAMS_CLASSES,
    TransformParams,
    MLTransformParams,
    ReportTransformParams,
    AnalysisTransformParams,
    TransformParamsT,
    MLTransformParamsT,
    ReportTransformParamsT,
    AnalysisTransformParamsT,
)

# ------------------- Load Params ------------------- #
from .load_params import (
    LOAD_PARAMS_CLASSES,
    LoadParams,
    ExcelLoadParams,
    SQLLoadParams,
    APILoadParams,
    LoadParamsT,
    ExcelLoadParamsT,
    SQLLoadParamsT,
    APILoadParamsT,
)

# ------------------- __all__ ------------------- #
__all__ = [
    "Params",
    # Extract Params
    "EXTRACT_PARAMS_CLASSES",
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
    # Transform Params
    "TRANSFORM_PARAMS_CLASSES",
    "TransformParams",
    "MLTransformParams",
    "ReportTransformParams",
    "AnalysisTransformParams",
    "TransformParamsT",
    "MLTransformParamsT",
    "ReportTransformParamsT",
    "AnalysisTransformParamsT",
    # Load Params
    "LOAD_PARAMS_CLASSES",
    "LoadParams",
    "ExcelLoadParams",
    "SQLLoadParams",
    "APILoadParams",
    "LoadParamsT",
    "ExcelLoadParamsT",
    "SQLLoadParamsT",
    "APILoadParamsT",
]
