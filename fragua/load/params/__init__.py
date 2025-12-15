"""
Load Params Module.

This module contains:
- LoadParams base class.
- Load CSV, excel, API & SQL Params class.
- Generic types for each Params class(e.g. LoadParamsT).
- Dict registry with each Params class.('name': class)
"""

from .base import LoadParams


from .load_params import (
    ExcelLoadParams,
    APILoadParams,
    SQLLoadParams,
    LOAD_PARAMS_CLASSES,
)

from .generic_types import (
    LoadParamsT,
    ExcelLoadParamsT,
    SQLLoadParamsT,
    APILoadParamsT,
)


__all__ = [
    "LoadParams",
    "ExcelLoadParams",
    "SQLLoadParams",
    "APILoadParams",
    "LoadParamsT",
    "ExcelLoadParamsT",
    "SQLLoadParamsT",
    "APILoadParamsT",
    "LOAD_PARAMS_CLASSES",
]
