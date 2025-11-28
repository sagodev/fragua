"""
ExtractStyle types for various data extraction methods.
"""

from typing import Any, Generic, Dict
import pandas as pd

from fragua.functions.extract_functions import (
    APIExtractFunction,
    CSVExtractFunction,
    ExcelExtractFunction,
    SQLExtractFunction,
)
from fragua.core.style import Style, ResultT
from fragua.extract.extract_params import (
    ExtractParams,
    ExtractParamsT,
    CSVExtractParamsT,
    ExcelExtractParamsT,
    SQLExtractParamsT,
    APIExtractParamsT,
)

from fragua.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------- #
# Base ExtractStyle
# ---------------------------------------------------------------------- #
class ExtractStyle(Style[ExtractParamsT, ResultT], Generic[ExtractParamsT, ResultT]):
    """
    Base class for all extraction styles in Fragua ETL.

    Standard pipeline provided by Style:
        validate_params -> _run -> validate_result -> postprocess
    """

    def extract(self, params: ExtractParamsT) -> ResultT:
        """
        Base extract method. Should be implemented by subclasses
        to call the appropriate registered function.
        """
        raise NotImplementedError

    def _run(self, params: ExtractParamsT) -> ResultT:
        logger.debug("Starting ExtractStyle '%s' extraction.", self.style_name)
        result = self.extract(params)
        logger.debug("ExtractStyle '%s' extraction completed.", self.style_name)
        return result


# ---------------------------------------------------------------------- #
# CSV Extraction
# ---------------------------------------------------------------------- #
class CSVExtractStyle(ExtractStyle[CSVExtractParamsT, pd.DataFrame]):
    """Extracts data from CSV files."""

    def extract(self, params: CSVExtractParamsT) -> pd.DataFrame:
        return CSVExtractFunction("extract_csv", params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        return {
            "style_name": "csv",
            "purpose": "Extract tabular data from CSV files.",
            "action": "extract",
            "parameters_type": "CSVExtractParams",
            "pipeline": ["CSVExtractFunction"],
            "fields": {
                "path": "Path to the CSV file.",
                "read_kwargs": "Additional read_csv() keyword arguments.",
            },
        }


# ---------------------------------------------------------------------- #
# Excel Extraction
# ---------------------------------------------------------------------- #
class ExcelExtractStyle(ExtractStyle[ExcelExtractParamsT, pd.DataFrame]):
    """Extracts data from Excel files."""

    def extract(self, params: ExcelExtractParamsT) -> pd.DataFrame:
        return ExcelExtractFunction("extract_excel", params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        return {
            "style_name": "excel",
            "purpose": "Extract structured data from Excel spreadsheets.",
            "action": "extract",
            "parameters_type": "ExcelExtractParams",
            "pipeline": ["ExcelExtractFunction"],
            "fields": {
                "path": "Path to the Excel file.",
                "sheet_name": "Worksheet to load.",
                "read_kwargs": "Additional pandas read_excel() options.",
            },
        }


# ---------------------------------------------------------------------- #
# SQL Extraction
# ---------------------------------------------------------------------- #
class SQLExtractStyle(ExtractStyle[SQLExtractParamsT, pd.DataFrame]):
    """Extracts data from SQL databases."""

    def extract(self, params: SQLExtractParamsT) -> pd.DataFrame:
        return SQLExtractFunction("extract_sql", params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        return {
            "style_name": "sql",
            "purpose": "Extract records from SQL databases using queries.",
            "action": "extract",
            "parameters_type": "SQLExtractParams",
            "pipeline": ["SQLExtractFunction"],
            "fields": {
                "connection_string": "Database connection string.",
                "query": "SQL query to execute.",
            },
        }


# ---------------------------------------------------------------------- #
# API Extraction
# ---------------------------------------------------------------------- #
class APIExtractStyle(ExtractStyle[APIExtractParamsT, pd.DataFrame]):
    """Extracts data from REST APIs."""

    def extract(self, params: APIExtractParamsT) -> pd.DataFrame:
        return APIExtractFunction("extract_api", params).execute()

    def summary_fields(self) -> Dict[str, Any]:
        return {
            "style_name": "api",
            "purpose": "Extract data from REST APIs over HTTP.",
            "action": "extract",
            "parameters_type": "APIExtractParams",
            "pipeline": ["APIExtractFunction"],
            "fields": {
                "url": "Request endpoint.",
                "method": "HTTP method (GET, POST, etc.).",
                "headers": "Request headers.",
                "params": "URL query parameters.",
                "data": "Request body.",
                "timeout": "Timeout for request.",
            },
        }


EXTRACT_STYLE_CLASSES: Dict[str, type[ExtractStyle[ExtractParams, Any]]] = {
    "csv": CSVExtractStyle,
    "excel": ExcelExtractStyle,
    "sql": SQLExtractStyle,
    "api": APIExtractStyle,
}
