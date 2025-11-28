"""Extract Styles Registry."""

from typing import Any, Dict

from fragua.extract.params.base import ExtractParams
from fragua.extract.styles.base import ExtractStyle
from fragua.extract.styles.extract_styles import (
    APIExtractStyle,
    CSVExtractStyle,
    ExcelExtractStyle,
    SQLExtractStyle,
)


EXTRACT_STYLE_CLASSES: Dict[str, type[ExtractStyle[ExtractParams, Any]]] = {
    "csv": CSVExtractStyle,
    "excel": ExcelExtractStyle,
    "sql": SQLExtractStyle,
    "api": APIExtractStyle,
}
