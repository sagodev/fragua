"""
ExtractStyle types for various data extraction methods, refactored to use FUNCTION_REGISTRY.
"""

from typing import Generic
import pandas as pd

from fragua.styles.style import Style, ResultT, register_style
from fragua.params.extract_params import (
    ExtractParamsT,
    CSVExtractParamsT,
    ExcelExtractParamsT,
    SQLExtractParamsT,
    APIExtractParamsT,
)
from fragua.functions.function import get_function
from fragua.utils.logger import get_logger

logger = get_logger(__name__)
action: str = "extract"


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
        """
        Executes the ExtractStyle extraction step.

        This method is called by Style.use().
        """
        logger.debug("Starting ExtractStyle '%s' extraction.", self.style_name)
        result = self.extract(params)
        logger.debug("ExtractStyle '%s' extraction completed.", self.style_name)
        return result


# ---------------------------------------------------------------------- #
# CSV Extraction
# ---------------------------------------------------------------------- #
@register_style(action, "csv")
class CSVExtractStyle(ExtractStyle[CSVExtractParamsT, pd.DataFrame]):
    """Extracts data from CSV files."""

    def extract(self, params: CSVExtractParamsT) -> pd.DataFrame:
        func = get_function(action, "Extract_csv")
        return func(params)


# ---------------------------------------------------------------------- #
# Excel Extraction
# ---------------------------------------------------------------------- #
@register_style(action, "excel")
class ExcelExtractStyle(ExtractStyle[ExcelExtractParamsT, pd.DataFrame]):
    """Extracts data from Excel files."""

    def extract(self, params: ExcelExtractParamsT) -> pd.DataFrame:
        func = get_function(action, "extract_excel")
        return func(params)


# ---------------------------------------------------------------------- #
# SQL Extraction
# ---------------------------------------------------------------------- #
@register_style(action, "sql")
class SQLExtractStyle(ExtractStyle[SQLExtractParamsT, pd.DataFrame]):
    """Extracts data from SQL databases."""

    def extract(self, params: SQLExtractParamsT) -> pd.DataFrame:
        func = get_function(action, "extract_sql")
        return func(params)


# ---------------------------------------------------------------------- #
# API Extraction
# ---------------------------------------------------------------------- #
@register_style(action, "api")
class APIExtractStyle(ExtractStyle[APIExtractParamsT, pd.DataFrame]):
    """Extracts data from REST APIs."""

    def extract(self, params: APIExtractParamsT) -> pd.DataFrame:
        func = get_function(action, "extract_api")
        return func(params)
