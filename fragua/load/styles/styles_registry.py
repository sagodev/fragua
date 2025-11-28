"""Load Styles Registry."""

from typing import Any, Dict

from fragua.load.params.base import LoadParams
from fragua.load.styles.base import LoadStyle
from fragua.load.styles.load_styles import ExcelLoadStyle


LOAD_STYLE_CLASSES: Dict[str, type[LoadStyle[LoadParams, Any]]] = {
    "excel": ExcelLoadStyle,
}
