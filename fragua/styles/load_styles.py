"""
LoadStyle types for various data Load methods.
"""

from abc import abstractmethod
from typing import Any, Generic
import pandas as pd


from fragua.styles.style import Style, ResultT, register_style
from fragua.params.load_params import (
    LoadParamsT,
    ExcelLoadParamsT,
    SQLLoadParamsT,
    APILoadParamsT,
)
from fragua.utils.logger import get_logger
from fragua.functions.function import get_function

logger = get_logger(__name__)

action: str = "load"


# ---------------------------------------------------------------------- #
# Base LoadStyle
# ---------------------------------------------------------------------- #
class LoadStyle(Style[LoadParamsT, ResultT], Generic[LoadParamsT, ResultT]):
    """
    Base class for all Load styles in Fragua ETL.

    Standard pipeline provided by Style:
        validate_params -> _run -> validate_result -> postprocess
    """

    @abstractmethod
    def load(self, params: LoadParamsT) -> ResultT:
        """
        load the given data to the target destination.
        Must be overridden by subclasses or use function registry.
        """
        raise NotImplementedError("Subclasses must implement load()")

    def _run(self, params: LoadParamsT) -> ResultT:
        """
        Executes the LoadStyle Load step.
        """
        logger.debug("Starting LoadStyle '%s' Load.", self.style_name)
        result = self.load(params)
        logger.debug("LoadStyle '%s' Load completed.", self.style_name)
        return result


# ---------------------------------------------------------------------- #
# Excel Load
# ---------------------------------------------------------------------- #
@register_style(action, "excel")
class ExcelLoadStyle(LoadStyle[ExcelLoadParamsT, pd.DataFrame]):
    """
    LoadStyle for exporting data to Excel files.
    Uses registered functions for pipeline steps.
    """

    def load(self, params: ExcelLoadParamsT) -> pd.DataFrame:
        load_func = get_function(action, "load_excel")
        return load_func(params)


# ---------------------------------------------------------------------- #
# SQL Load
# ---------------------------------------------------------------------- #
@register_style(action, "sql")
class SQLLoadStyle(LoadStyle[SQLLoadParamsT, pd.DataFrame]):
    """
    LoadStyle for loading data to SQL databases.
    Uses registered functions for pipeline steps.
    """

    def load(self, params: SQLLoadParamsT) -> pd.DataFrame:
        load_func = get_function(action, "load_sql")
        return load_func(params)


# ---------------------------------------------------------------------- #
# API Load
# ---------------------------------------------------------------------- #
@register_style(action, "api")
class APILoadStyle(LoadStyle[APILoadParamsT, Any]):
    """
    LoadStyle for loading data to external APIs.
    Uses registered functions for pipeline steps.
    """

    def load(self, params: APILoadParamsT) -> Any:
        load_func = get_function(action, "load_api")
        return load_func(params)
