"""Load Params Registry."""

from typing import Dict
from fragua.load.params.base import LoadParams
from fragua.load.params.load_params import APILoadParams, ExcelLoadParams, SQLLoadParams


LOAD_PARAMS_CLASSES: Dict[str, type[LoadParams]] = {
    "excel": ExcelLoadParams,
    "sql": SQLLoadParams,
    "api": APILoadParams,
}
