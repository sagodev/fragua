"""
Extract Params Module.

This module contains:
- ExtractParams base class.
- Extract CSV, excel, API & SQL Params class.
- Generic types for each Params class(e.g. ExtractParamsT).
- Dict registry with each Params class.('name': class)
"""

from .base import ExtractParams


from .extract_params import (
    CSVExtractParams,
    ExcelExtractParams,
    APIExtractParams,
    SQLExtractParams,
    EXTRACT_PARAMS_CLASSES,
)

from .generic_types import (
    ExtractParamsT,
    CSVExtractParamsT,
    ExcelExtractParamsT,
    SQLExtractParamsT,
    APIExtractParamsT,
)


__all__ = [
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
    "EXTRACT_PARAMS_CLASSES",
]
