"""
Load function implementations.

This module defines concrete LoadFunction classes responsible
for persisting processed data into external destinations.
Each function encapsulates the low-level persistence logic
for a specific target system or format.
"""

from typing import Any, Dict, Optional, Type
import pandas as pd

from fragua.load.functions.base import LoadFunction
from fragua.load.functions.internal_functions import (
    build_excel_path,
    convert_datetime_columns,
    validate_excel_params,
    write_excel,
)
from fragua.load.params.load_params import ExcelLoadParams


class ExcelLoadFunction(LoadFunction):
    """
    LoadFunction implementation for Excel outputs.

    This function:
    - validates Excel-specific parameters
    - resolves the target file path
    - normalizes datetime columns for compatibility
    - writes the data into an Excel file
    """

    PURPOSE: str = "Export a DataFrame to an Excel file."

    def __init__(self, params: Optional[ExcelLoadParams] = None) -> None:
        """
        Initialize the Excel load function.

        Args:
            params (Optional[ExcelLoadParams]):
                Parameters controlling Excel output behavior.
                If not provided, a default ExcelLoadParams instance is created.
        """
        super().__init__()
        self.params = ExcelLoadParams() if params is None else params

    def execute(self) -> pd.DataFrame:
        """
        Execute the Excel load operation.

        Performs the full persistence workflow:
        - parameter validation
        - destination path construction
        - datetime normalization
        - Excel file writing

        Returns:
            pd.DataFrame: The DataFrame that was persisted.
        """
        validate_excel_params(self.params)
        path = build_excel_path(self.params)
        df = convert_datetime_columns(self.params.data)
        write_excel(df, path, self.params.sheet_name or "Sheet1", self.params.index)
        return df

    def summary(self) -> dict[str, Any]:
        """
        Return a structured summary of the Excel load function.

        Includes:
            - function name
            - associated parameter class
            - functional purpose
        """
        return {
            "name": self.name,
            "params_type": type(self.params).__name__,
            "purpose": self.PURPOSE,
        }


LOAD_FUNCTION_CLASSES: Dict[str, Type[LoadFunction]] = {
    "excel": ExcelLoadFunction,
}
