"""Fragua Styles package."""

# ------------------- Load Style Types ------------------- #
from .load_styles import (
    LOAD_STYLE_CLASSES,
    LoadStyle,
    ExcelLoadStyle,
)


# ------------------- __all__ ------------------- #
__all__ = [
    "LoadStyle",
    # Load Styles
    "LOAD_STYLE_CLASSES",
    "ExcelLoadStyle",
]
