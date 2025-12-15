"""
Extract Styles Module.

This module contains:
- ExtractStyle base class.
- Extract CSV, excel, API & SQL Style class.
- Dict registry with each Style class.('name': class)
"""

from .base import ExtractStyle

from .extract_styles import (
    CSVExtractStyle,
    ExcelExtractStyle,
    SQLExtractStyle,
    APIExtractStyle,
    EXTRACT_STYLE_CLASSES,
)


__all__ = [
    "ExtractStyle",
    "CSVExtractStyle",
    "ExcelExtractStyle",
    "SQLExtractStyle",
    "APIExtractStyle",
    "EXTRACT_STYLE_CLASSES",
]
