"""
ExtractStyle types for various data extraction methods.
"""

from typing import Any, Dict, Type
import pandas as pd

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
from fragua.extract.styles.base import ExtractStyle


class CSVExtractStyle(ExtractStyle):
    """Extracts data from CSV files."""

    def extract(self, params: CSVExtractParams) -> pd.DataFrame:
        return CSVExtractFunction(params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        return {
            "style_name": self.__class__.__name__,
            "purpose": "Extract tabular data from CSV files.",
            "action": "extract",
            "parameters_type": "CSVExtractParams",
            "function": "CSVExtractFunction",
            "fields": {
                "path": "Path to the CSV file.",
            },
        }


class ExcelExtractStyle(ExtractStyle):
    """Extracts data from Excel files."""

    def extract(self, params: ExcelExtractParams) -> pd.DataFrame:
        return ExcelExtractFunction(params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        return {
            "style_name": self.__class__.__name__,
            "purpose": "Extract structured data from Excel spreadsheets.",
            "action": "extract",
            "parameters_type": "ExcelExtractParams",
            "function": "ExcelExtractFunction",
            "fields": {
                "path": "Path to the Excel file.",
                "sheet_name": "Worksheet to load.",
            },
        }


class SQLExtractStyle(ExtractStyle):
    """Extracts data from SQL databases."""

    def extract(self, params: SQLExtractParams) -> pd.DataFrame:
        return SQLExtractFunction(params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        return {
            "style_name": self.__class__.__name__,
            "purpose": "Extract records from SQL databases using queries.",
            "action": "extract",
            "parameters_type": "SQLExtractParams",
            "function": "SQLExtractFunction",
            "fields": {
                "connection_string": "Database connection string.",
                "query": "SQL query to execute.",
            },
        }


class APIExtractStyle(ExtractStyle):
    """Extracts data from REST APIs."""

    def extract(self, params: APIExtractParams) -> pd.DataFrame:
        return APIExtractFunction(params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        return {
            "style_name": self.__class__.__name__,
            "purpose": "Extract data from REST APIs over HTTP.",
            "action": "extract",
            "parameters_type": "APIExtractParams",
            "function": "APIExtractFunction",
            "fields": {
                "url": "Request endpoint.",
                "method": "HTTP method (GET, POST, etc.).",
                "headers": "Request headers.",
                "params": "URL query parameters.",
                "data": "Request body.",
                "timeout": "Timeout for request.",
            },
        }


EXTRACT_STYLE_CLASSES: Dict[str, Type[ExtractStyle]] = {
    "csv": CSVExtractStyle,
    "excel": ExcelExtractStyle,
    "sql": SQLExtractStyle,
    "api": APIExtractStyle,
}
