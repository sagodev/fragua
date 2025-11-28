"""Extract Params Registry."""

from typing import Dict
from fragua.extract.params.base import ExtractParams
from fragua.extract.params.extract_params import (
    APIExtractParams,
    CSVExtractParams,
    ExcelExtractParams,
    SQLExtractParams,
)


EXTRACT_PARAMS_CLASSES: Dict[str, type[ExtractParams]] = {
    "csv": CSVExtractParams,
    "excel": ExcelExtractParams,
    "sql": SQLExtractParams,
    "api": APIExtractParams,
}
