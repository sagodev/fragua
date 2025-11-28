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

# ------------------- Extract Styles ------------------- #
from ..extract.extract_styles import (
    EXTRACT_STYLE_CLASSES,
    ExtractStyle,
    CSVExtractStyle,
    ExcelExtractStyle,
    SQLExtractStyle,
    APIExtractStyle,
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

# ------------------- Extractor Agent ------------------- #
from .extractor import Extractor

__all__ = [
    # Extractor Agent
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
    # Extract Styles
    "ExtractStyle",
    "EXTRACT_STYLE_CLASSES",
    "CSVExtractStyle",
    "ExcelExtractStyle",
    "SQLExtractStyle",
    "APIExtractStyle",
]
