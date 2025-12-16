"""
Load Params Module.

This module contains:
- LoadParams base class.
- Load CSV, excel, API & SQL Params class.
- Generic types for each Params class(e.g. LoadParamsT).
- Dict registry with each Params class.('name': class)
"""

from .load_params import (
    ExcelLoadParams,
    APILoadParams,
    SQLLoadParams,
    LOAD_PARAMS_SCHEMAS,
)


__all__ = [
    "ExcelLoadParams",
    "SQLLoadParams",
    "APILoadParams",
    "LOAD_PARAMS_SCHEMAS",
]
