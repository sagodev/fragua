"""
LoadStyle types for various data Load methods.
"""

from typing import Any, Dict, Type
import pandas as pd

from fragua.core.style import FraguaStyle
from fragua.load.functions.load_functions import (
    APILoadFunction,
    CSVLoadFunction,
    ExcelLoadFunction,
    SQLLoadFunction,
)
from fragua.load.params.load_params import (
    APILoadParams,
    CSVLoadParams,
    ExcelLoadParams,
    SQLLoadParams,
)


class ExcelLoadStyle(FraguaStyle[ExcelLoadParams]):
    """
    Load style for exporting tabular data to Excel files.

    Delegates the loading logic to ExcelLoadFunction.
    """

    action = "load"
    function = ExcelLoadFunction.__name__
    params_type = ExcelLoadParams.__name__
    purpose = "Export tabular data to an Excel file."

    def execute(
        self,
        params: ExcelLoadParams,
        input_data: pd.DataFrame | None = None,
        context: Any = None,
    ) -> pd.DataFrame:
        """
        Execute the Excel load operation.

        Args:
            params (ExcelLoadParams): Parameters defining the Excel output configuration.
            input_data (pd.DataFrame | None): DataFrame to be written.
            context (Any): Optional runtime context.

        Returns:
            pd.DataFrame: The DataFrame that was persisted.
        """
        df = pd.DataFrame() if input_data is None else input_data

        return ExcelLoadFunction().execute(
            input_data=df, params=params, context=context
        )


class CSVLoadStyle(FraguaStyle[CSVLoadParams]):
    """
    Load style for exporting tabular data to CSV files.

    Delegates the loading logic to CSVLoadFunction.
    """

    action = "load"
    function = SQLLoadFunction.__name__
    params_type = CSVLoadParams.__name__
    purpose = "Export tabular data to a CSV file."

    def execute(
        self,
        params: CSVLoadParams,
        input_data: pd.DataFrame | None = None,
        context: Any = None,
    ) -> pd.DataFrame:
        """
        Execute the CSV load operation.

        Args:
            params (CSVLoadParams): Parameters defining the CSV output configuration.
            input_data (pd.DataFrame | None): DataFrame to be written.
            context (Any): Optional runtime context.

        Returns:
            pd.DataFrame: The DataFrame that was persisted.
        """
        df = pd.DataFrame() if input_data is None else input_data

        return CSVLoadFunction().execute(input_data=df, params=params, context=context)


class SQLLoadStyle(FraguaStyle[SQLLoadParams]):
    """
    Load style for inserting or updating tabular data in a SQL database.

    Delegates the loading logic to SQLLoadFunction.
    """

    action = "load"
    function = SQLLoadFunction.__name__
    params_type = SQLLoadParams.__name__
    purpose = "Load tabular data into a SQL database."

    def execute(
        self,
        params: SQLLoadParams,
        input_data: pd.DataFrame | None = None,
        context: Any = None,
    ) -> pd.DataFrame:
        """
        Execute the SQL load operation.

        Args:
            params (SQLLoadParams): Parameters defining the SQL target configuration.
            input_data (pd.DataFrame | None): DataFrame to be loaded.
            context (Any): Optional runtime context.

        Returns:
            pd.DataFrame: The DataFrame that was persisted.
        """
        df = pd.DataFrame() if input_data is None else input_data

        return SQLLoadFunction().execute(input_data=df, params=params, context=context)


class APILoadStyle(FraguaStyle[APILoadParams]):
    """
    Load style for sending tabular data to a REST API endpoint.

    Delegates the loading logic to APILoadFunction.
    """

    action = "load"
    function = APILoadFunction.__name__
    params_type = APILoadParams.__name__
    purpose = "Send tabular data to a REST API over HTTP."

    def execute(
        self,
        params: APILoadParams,
        input_data: pd.DataFrame | None = None,
        context: Any = None,
    ) -> pd.DataFrame:
        """
        Execute the API load operation.

        Args:
            params (APILoadParams): Parameters defining the API target configuration.
            input_data (pd.DataFrame | None): DataFrame to be sent.
            context (Any): Optional runtime context.

        Returns:
            pd.DataFrame: The DataFrame that was sent (as a reference or confirmation).
        """
        df = pd.DataFrame() if input_data is None else input_data

        return APILoadFunction().execute(input_data=df, params=params, context=context)


LOAD_STYLE_CLASSES: Dict[str, Type[FraguaStyle]] = {
    "excel": ExcelLoadStyle,
    "csv": CSVLoadStyle,
    "sql": SQLLoadStyle,
    "api": APILoadStyle,
}
