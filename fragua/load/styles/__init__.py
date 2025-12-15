"""
Load Styles Module.

This module contains:
- ExtractStyle base class.
- Load CSV, excel, API & SQL Style class.
- Dict registry with each Style class.('name': class)
"""

from .base import LoadStyle

from .load_styles import ExcelLoadStyle, LOAD_STYLE_CLASSES


__all__ = [
    "LoadStyle",
    "ExcelLoadStyle",
    "LOAD_STYLE_CLASSES",
]
