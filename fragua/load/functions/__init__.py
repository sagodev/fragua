"""
Load Functions Module.

This module contains:
- LoadFunction base class.
- Load excel Function class.
- Dict registry with each Function class. ('name': class)
- Dict registry with each internal function. ('name': function(Callable))
"""

from .base import LoadFunction

from .load_functions import ExcelLoadFunction, LOAD_FUNCTION_CLASSES
from .internal_functions import LOAD_INTERNAL_FUNCTIONS


__all__ = [
    "LoadFunction",
    "ExcelLoadFunction",
    "LOAD_FUNCTION_CLASSES",
    "LOAD_INTERNAL_FUNCTIONS",
]
