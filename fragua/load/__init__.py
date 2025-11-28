"""
Load module.

This module contains:
- Loader agent subclass.
- Load Params subclasses.
- Load Style subclasses.
- Load FraguaFunctions subclasses.
"""

# ------------------- Load Functions ------------------- #
from .load_functions import (
    LOAD_FUNCTION_CLASSES,
    LoadFunction,
    ExcelLoadFunction,
)

# ------------------- Load Styles ------------------- #
from .load_styles import (
    LOAD_STYLE_CLASSES,
    LoadStyle,
    ExcelLoadStyle,
)

# ------------------- Load Params ------------------- #


# ------------------- Load Agent ------------------- #
from .loader import Loader


__all__ = [
    # Loader Agent
    "Loader",
    # Load Params
    # Load Functions
    "LOAD_FUNCTION_CLASSES",
    "LoadFunction",
    "ExcelLoadFunction",
    # Load Styles
    "LOAD_STYLE_CLASSES",
    "LoadStyle",
    "ExcelLoadStyle",
]
