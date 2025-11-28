"""Load Function Registry."""

from typing import Any, Callable, Dict

from fragua.load.functions.base import LoadFunction
from fragua.load.functions.internal_functions import (
    build_excel_path,
    convert_datetime_columns,
    validate_excel_params,
    write_excel,
)
from fragua.load.functions.load_functions import ExcelLoadFunction
from fragua.load.params.load_params import LoadParams


LOAD_INTERNAL_FUNCTIONS: Dict[str, Callable[..., Any]] = {
    "validate_excel_params": validate_excel_params,
    "build_excel_path": build_excel_path,
    "convert_datetime_columns": convert_datetime_columns,
    "write_excel": write_excel,
}

LOAD_FUNCTION_CLASSES: Dict[str, type[LoadFunction[LoadParams]]] = {
    "excel": ExcelLoadFunction,
}
