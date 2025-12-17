"""
Concrete ExtractStyle implementations for different data sources.

Each ExtractStyle coordinates a specific extraction workflow by:
- receiving typed ExtractParams
- delegating execution to the corresponding ExtractFunction
- returning extracted data as a pandas DataFrame
"""

from typing import Any, Dict, Type
import pandas as pd

from fragua.core.style import FraguaStyle
from fragua.extract.functions.extract_functions import (
    APIExtractFunction,
    CSVExtractFunction,
    ExcelExtractFunction,
    SQLExtractFunction,
)
from fragua.extract.params.extract_params import (
    APIExtractParams,
    CSVExtractParams,
    ExcelExtractParams,
    SQLExtractParams,
)


class CSVExtractStyle(FraguaStyle[CSVExtractParams]):
    """
    Extraction style for CSV-based data sources.

    Delegates the extraction logic to CSVExtractFunction.
    """

    action = "extract"
    function = CSVExtractFunction.__name__
    params_type = CSVExtractParams.__name__
    purpose = "Extract tabular data from CSV files."

    def execute(
        self, params: CSVExtractParams, input_data: None = None, context: Any = None
    ) -> pd.DataFrame:
        """
        Execute CSV extraction.

        Args:
            params (CSVExtractParamsT): Parameters defining the CSV source.
            input_data: Not used for CSV extraction (default: None).
            context: Optional runtime context (default: None).

        Returns:
            pd.DataFrame: Extracted tabular data from the CSV file.
        """
        return CSVExtractFunction().execute(
            input_data=input_data, params=params, context=context
        )


class ExcelExtractStyle(FraguaStyle[ExcelExtractParams]):
    """
    Extraction style for Excel-based data sources.

    Delegates the extraction logic to ExcelExtractFunction.
    """

    action = "extract"
    function = ExcelExtractFunction.__name__
    params_type = ExcelExtractParams.__name__
    purpose = "Extract structured data from Excel spreadsheets."

    def execute(
        self, params: ExcelExtractParams, input_data: None = None, context: Any = None
    ) -> pd.DataFrame:
        """
        Execute Excel extraction.

        Args:
            params (ExcelExtractParamsT): Parameters defining the Excel source.
            input_data: Not used for Excel extraction (default: None).
            context: Optional runtime context (default: None).

        Returns:
            pd.DataFrame: Extracted worksheet data.
        """
        return ExcelExtractFunction().execute(
            input_data=input_data, params=params, context=context
        )


class SQLExtractStyle(FraguaStyle[SQLExtractParams]):
    """
    Extraction style for SQL database sources.

    Delegates the query execution to SQLExtractFunction.
    """

    action = "extract"
    function = SQLExtractFunction.__name__
    params_type = SQLExtractParams.__name__
    purpose = "Extract records from SQL databases using queries."

    def execute(
        self, params: SQLExtractParams, input_data: None = None, context: Any = None
    ) -> pd.DataFrame:
        """
        Execute SQL extraction.

        Args:
            params (SQLExtractParamsT): Parameters defining database connection and query.
            input_data: Not used for SQL extraction (default: None).
            context: Optional runtime context (default: None).

        Returns:
            pd.DataFrame: Result of the SQL query.
        """
        return SQLExtractFunction().execute(
            input_data=input_data, params=params, context=context
        )


class APIExtractStyle(FraguaStyle[APIExtractParams]):
    """
    Extraction style for REST API data sources.

    Delegates HTTP requests and JSON parsing to APIExtractFunction.
    """

    action = "extract"
    function = APIExtractFunction.__name__
    params_type = APIExtractParams.__name__
    purpose = "Extract data from REST APIs over HTTP."

    def execute(
        self, params: APIExtractParams, input_data: None = None, context: Any = None
    ) -> pd.DataFrame:
        """
        Execute API extraction.

        Args:
            params (APIExtractParamsT): Parameters defining the API request.
            input_data: Not used for API extraction (default: None).
            context: Optional runtime context (default: None).

        Returns:
            pd.DataFrame: Extracted data from the API response.
        """
        return APIExtractFunction().execute(
            input_data=input_data, params=params, context=context
        )


EXTRACT_STYLE_CLASSES: Dict[str, Type[FraguaStyle]] = {
    "csv": CSVExtractStyle,
    "excel": ExcelExtractStyle,
    "sql": SQLExtractStyle,
    "api": APIExtractStyle,
}
