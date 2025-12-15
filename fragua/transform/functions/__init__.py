"""
Transform Functions Module.

This module contains:
- TransformFunction base class.
- Transform Analysis, Report, ML Function class.
- Dict registry with each Function class.('name': class)
- Dict registry with each internal function. ('name': function(Callable))
"""

from .base import TransformFunction

from .internal_functions import (
    TRANSFORM_INTERNAL_FUNCTIONS,
)


from .transform_functions import (
    AnalysisTransformFunction,
    ReportTransformFunction,
    MLTransformFunction,
    TRANSFORM_FUNCTION_CLASSES,
)


__all__ = [
    "TransformFunction",
    "AnalysisTransformFunction",
    "ReportTransformFunction",
    "MLTransformFunction",
    "TRANSFORM_FUNCTION_CLASSES",
    "TRANSFORM_INTERNAL_FUNCTIONS",
]
