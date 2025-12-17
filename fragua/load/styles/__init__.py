"""
Load Styles Module.

This module contains:
- ExtractStyle base class.
- Load CSV, excel, API & SQL Style class.
- Dict registry with each Style class.('name': class)
"""

from .load_styles import (
    ExcelLoadStyle,
    SQLLoadStyle,
    APILoadStyle,
    CSVLoadStyle,
    LOAD_STYLE_CLASSES,
)


__all__ = [
    "ExcelLoadStyle",
    "CSVLoadStyle",
    "SQLLoadStyle",
    "APILoadStyle",
    "LOAD_STYLE_CLASSES",
]
