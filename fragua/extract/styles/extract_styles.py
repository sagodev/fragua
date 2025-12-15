"""
Concrete ExtractStyle implementations for different data sources.

Each ExtractStyle coordinates a specific extraction workflow by:
- receiving typed ExtractParams
- delegating execution to the corresponding ExtractFunction
- returning extracted data as a pandas DataFrame
"""

from typing import Any, Dict, Type
import pandas as pd

from fragua.extract.functions.extract_functions import (
    APIExtractFunction,
    CSVExtractFunction,
    ExcelExtractFunction,
    SQLExtractFunction,
)
from fragua.extract.params.base import ExtractParams
from fragua.extract.params.extract_params import (
    APIExtractParams,
    CSVExtractParams,
    ExcelExtractParams,
    SQLExtractParams,
)
from fragua.extract.params.generic_types import (
    APIExtractParamsT,
    CSVExtractParamsT,
    ExcelExtractParamsT,
    SQLExtractParamsT,
)
from fragua.extract.styles.base import ExtractStyle


class CSVExtractStyle(ExtractStyle[CSVExtractParamsT]):
    """
    Extraction style for CSV-based data sources.

    Orchestrates CSV data extraction by delegating execution
    to CSVExtractFunction using CSVExtractParams.
    """

    def extract(self, params: CSVExtractParams) -> pd.DataFrame:
        """
        Extract tabular data from a CSV file.

        Args:
            params (CSVExtractParams): Parameters defining the CSV source.

        Returns:
            pd.DataFrame: Extracted tabular data.
        """
        return CSVExtractFunction(params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        """
        Return metadata describing this extract style.
        """
        return {
            "style_name": self.__class__.__name__,
            "purpose": "Extract tabular data from CSV files.",
            "action": "extract",
            "parameters_type": "CSVExtractParams",
            "function": "CSVExtractFunction",
            "fields": {
                "path": "Filesystem path to the CSV file.",
            },
        }


class ExcelExtractStyle(ExtractStyle[ExcelExtractParamsT]):
    """
    Extraction style for Excel-based data sources.

    Coordinates extraction from Excel spreadsheets via
    ExcelExtractFunction and ExcelExtractParams.
    """

    def extract(self, params: ExcelExtractParams) -> pd.DataFrame:
        """
        Extract structured data from an Excel spreadsheet.

        Args:
            params (ExcelExtractParams): Parameters defining the Excel source.

        Returns:
            pd.DataFrame: Extracted worksheet data.
        """
        return ExcelExtractFunction(params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        """
        Return metadata describing this extract style.
        """
        return {
            "style_name": self.__class__.__name__,
            "purpose": "Extract structured data from Excel spreadsheets.",
            "action": "extract",
            "parameters_type": "ExcelExtractParams",
            "function": "ExcelExtractFunction",
            "fields": {
                "path": "Filesystem path to the Excel file.",
                "sheet_name": "Worksheet name or index to load.",
            },
        }


class SQLExtractStyle(ExtractStyle[SQLExtractParamsT]):
    """
    Extraction style for SQL database sources.

    Orchestrates query-based extraction using SQLExtractFunction
    and SQLExtractParams.
    """

    def extract(self, params: SQLExtractParams) -> pd.DataFrame:
        """
        Execute a SQL query and extract its result set.

        Args:
            params (SQLExtractParams): Parameters defining database connection and query.

        Returns:
            pd.DataFrame: Query result as a DataFrame.
        """
        return SQLExtractFunction(params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        """
        Return metadata describing this extract style.
        """
        return {
            "style_name": self.__class__.__name__,
            "purpose": "Extract records from SQL databases using queries.",
            "action": "extract",
            "parameters_type": "SQLExtractParams",
            "function": "SQLExtractFunction",
            "fields": {
                "connection_string": "Database connection URL.",
                "query": "SQL query to execute.",
            },
        }


class APIExtractStyle(ExtractStyle[APIExtractParamsT]):
    """
    Extraction style for REST API data sources.

    Coordinates HTTP-based extraction workflows using
    APIExtractFunction and APIExtractParams.
    """

    def extract(self, params: APIExtractParams) -> pd.DataFrame:
        """
        Fetch and normalize data from a REST API endpoint.

        Args:
            params (APIExtractParams): Parameters defining the API request.

        Returns:
            pd.DataFrame: Extracted API response data.
        """
        return APIExtractFunction(params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        """
        Return metadata describing this extract style.
        """
        return {
            "style_name": self.__class__.__name__,
            "purpose": "Extract data from REST APIs over HTTP.",
            "action": "extract",
            "parameters_type": "APIExtractParams",
            "function": "APIExtractFunction",
            "fields": {
                "url": "Full API endpoint URL.",
                "method": "HTTP method (GET, POST, etc.).",
                "headers": "HTTP request headers.",
                "params": "URL query parameters.",
                "data": "Request body payload.",
                "timeout": "Maximum request timeout in seconds.",
            },
        }


EXTRACT_STYLE_CLASSES: Dict[str, Type[ExtractStyle[ExtractParams]]] = {
    "csv": CSVExtractStyle,
    "excel": ExcelExtractStyle,
    "sql": SQLExtractStyle,
    "api": APIExtractStyle,
}
