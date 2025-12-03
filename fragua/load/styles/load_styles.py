"""
LoadStyle types for various data Load methods.
"""

from typing import Any, Dict, Type
import pandas as pd

from fragua.load.functions.load_functions import ExcelLoadFunction

from fragua.load.params.base import LoadParams
from fragua.load.params.generic_types import ExcelLoadParamsT
from fragua.load.styles.base import LoadStyle


class ExcelLoadStyle(LoadStyle[ExcelLoadParamsT, pd.DataFrame]):
    """
    LoadStyle for exporting data to Excel files.
    Uses registered functions for pipeline steps.
    """

    def summary_fields(self) -> Dict[str, Any]:
        base = super().summary_fields()
        base.update(
            {
                "target": "Excel file",
                "fields": {
                    "output_path": "Output Excel file path.",
                    "sheet_name": "Excel sheet where data will be written.",
                    "index": "Whether to include DataFrame index.",
                },
                "function": "load_excel",
            }
        )
        return base

    def load(self, params: ExcelLoadParamsT) -> pd.DataFrame:
        return ExcelLoadFunction("load_excel", params).execute()


# ---------------------------------------------------------------------- #
# Future Styles (SQL, API, etc.)
# ---------------------------------------------------------------------- #
# No implementations yet.

LOAD_STYLE_CLASSES: Dict[str, Type[LoadStyle[LoadParams, Any]]] = {
    "excel": ExcelLoadStyle,
}
