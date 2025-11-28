"""Extract Function Registry."""

from typing import Dict

from fragua.extract.params.extract_params import ExtractParams

from .base import ExtractFunction
from .extract_functions import (
    CSVExtractFunction,
    ExcelExtractFunction,
    SQLExtractFunction,
    APIExtractFunction,
)


EXTRACT_FUNCTION_CLASSES: Dict[str, type[ExtractFunction[ExtractParams]]] = {
    "csv": CSVExtractFunction,
    "excel": ExcelExtractFunction,
    "sql": SQLExtractFunction,
    "api": APIExtractFunction,
}
