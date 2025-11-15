"""
Reusable Functions Module.
"""

# ------------------- Function class ------------------- #
from fragua.functions.function import (
    FraguaFunction,
)

# ------------------- Extract classes ------------------- #
from fragua.functions.extract_functions import (
    EXTRACT_FUNCTION_CLASSES,
    ExtractFunction,
    ExcelExtractFunction,
    APIExtractFunction,
    CSVExtractFunction,
    SQLExtractFunction,
)

# ------------------- Transform classes ------------------- #
from fragua.functions.transform_functions import (
    TRANSFORM_FUNCTION_CLASSES,
    TransformFunction,
    AnalysisTransformFunction,
    ReportTransformFunction,
    MLTransformFunction,
)

# ------------------- Load classes ------------------- #
from fragua.functions.load_functions import (
    LOAD_FUNCTION_CLASSES,
    LoadFunction,
    ExcelLoadFunction,
)

__all__ = [
    # Function class
    "FraguaFunction",
    # Extract classes
    "EXTRACT_FUNCTION_CLASSES",
    "ExtractFunction",
    "ExcelExtractFunction",
    "APIExtractFunction",
    "CSVExtractFunction",
    "SQLExtractFunction",
    # Transform classes
    "TRANSFORM_FUNCTION_CLASSES",
    "TransformFunction",
    "AnalysisTransformFunction",
    "ReportTransformFunction",
    "MLTransformFunction",
    # Load classes
    "LOAD_FUNCTION_CLASSES",
    "LoadFunction",
    "ExcelLoadFunction",
]
