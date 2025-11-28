"""
Extract module.

This module contains:
- Extractor agent subclass.
- Extract Params subclasses.
- Extract Style subclasses.
- Extract FraguaFunctions subclasses.
"""

# ------------------- Extract Functions ------------------- #
from fragua.extract.extract_functions import (
    EXTRACT_FUNCTION_CLASSES,
    ExtractFunction,
    ExcelExtractFunction,
    APIExtractFunction,
    CSVExtractFunction,
    SQLExtractFunction,
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

# ------------------- Extractor Subclass ------------------- #
from .extractor import Extractor

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
    # Extract Functions
    "EXTRACT_FUNCTION_CLASSES",
    "ExtractFunction",
    "ExcelExtractFunction",
    "APIExtractFunction",
    "CSVExtractFunction",
    "SQLExtractFunction",
]
