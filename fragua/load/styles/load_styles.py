"""
LoadStyle types for various data Load methods.
"""

from typing import Any, Dict, Type
import pandas as pd

from fragua.load.functions.load_functions import ExcelLoadFunction
from fragua.load.params.base import LoadParams
from fragua.load.params.generic_types import ExcelLoadParamsT
from fragua.load.params.load_params import ExcelLoadParams
from fragua.load.styles.base import LoadStyle


class ExcelLoadStyle(LoadStyle[ExcelLoadParamsT]):
    """
    Load style for exporting tabular data to Excel files.

    This style coordinates the loading process by delegating execution
    to the corresponding `ExcelLoadFunction`, using the parameters
    provided through an `ExcelLoadParams` instance.
    """

    def summary_fields(self) -> Dict[str, Any]:
        """
        Return a structured description of this load style.

        The summary provides metadata used for introspection,
        documentation, and configuration validation.

        Returns:
            Dict[str, Any]:
                Dictionary describing the style purpose, target,
                expected parameters, and underlying function.
        """
        return {
            "style_name": self.__class__.__name__,
            "purpose": "Export tabular data to an Excel file.",
            "action": "load",
            "target": "Excel file",
            "parameters_type": "ExcelLoadParams",
            "function": "ExcelLoadFunction",
            "fields": {
                "destination": "Directory where the Excel file will be written.",
                "file_name": "Name of the Excel file to create or overwrite.",
                "sheet_name": "Worksheet name where data will be written.",
                "index": "Whether to include DataFrame index.",
            },
        }

    def load(self, params: ExcelLoadParams) -> pd.DataFrame:
        """
        Execute the Excel load operation.

        This method delegates the actual writing logic to
        `ExcelLoadFunction`, returning the DataFrame that was persisted.

        Args:
            params (ExcelLoadParams):
                Parameters defining the Excel output configuration.

        Returns:
            pd.DataFrame:
                The DataFrame that was written to the Excel file.
        """
        return ExcelLoadFunction(params).execute()


# ---------------------------------------------------------------------- #
# Future Styles (SQL, API, etc.)
# ---------------------------------------------------------------------- #
# No implementations yet.

LOAD_STYLE_CLASSES: Dict[str, Type[LoadStyle[LoadParams]]] = {
    "excel": ExcelLoadStyle,
}
