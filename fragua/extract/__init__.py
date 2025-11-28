"""
Extract module.

This module contains:
- Extractor agent subclass.
- Extract Params subclasses.
- Extract Style subclasses.
- Extract FraguaFunctions subclasses.
"""
# ------------------- Extractor Subclass ------------------- #
from .extractor import Extractor

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

__all__ = [
    # Agent subclass
    "Extractor",
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
]
