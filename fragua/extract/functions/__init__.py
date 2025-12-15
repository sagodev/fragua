"""
Extract Functions Module.

This module contains:
- ExtractFunction base class.
- Extract CSV, excel, API & SQL Function class.
- Dict registry with each Function class.('name': class)
"""

from .base import ExtractFunction

from .extract_functions import (
    CSVExtractFunction,
    ExcelExtractFunction,
    SQLExtractFunction,
    APIExtractFunction,
    EXTRACT_FUNCTION_CLASSES,
)


__all__ = [
    "ExtractFunction",
    "ExcelExtractFunction",
    "APIExtractFunction",
    "CSVExtractFunction",
    "SQLExtractFunction",
    "EXTRACT_FUNCTION_CLASSES",
]
