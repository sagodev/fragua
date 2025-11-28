"""
LoadStyle types for various data Load methods.
"""

from abc import abstractmethod
from typing import Any, Dict, Generic
import pandas as pd

from fragua.load.load_functions import ExcelLoadFunction
from fragua.core.style import Style, ResultT
from fragua.load.load_params import (
    LoadParams,
    LoadParamsT,
    ExcelLoadParamsT,
)
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------- #
# Base LoadStyle
# ---------------------------------------------------------------------- #
class LoadStyle(Style[LoadParamsT, ResultT], Generic[LoadParamsT, ResultT]):
    """
    Base class for all Load styles in Fragua ETL.

    Standard pipeline provided by Style:
        validate_params -> _run -> validate_result -> postprocess
    """

    # ------------------------------------------------------------ #
    # Summary fields
    # ------------------------------------------------------------ #
    def summary_fields(self) -> Dict[str, Any]:
        """
        Returns metadata describing this LoadStyle.
        Each subclass should extend or override.
        """
        return {
            "style_type": "load",
            "description": "Handles loading data into external destinations.",
        }

    # ------------------------------------------------------------ #
    # Abstract load() method
    # ------------------------------------------------------------ #
    @abstractmethod
    def load(self, params: LoadParamsT) -> ResultT:
        """
        Load the given data to the target destination.
        Must be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement load()")

    # ------------------------------------------------------------ #
    # _run wrapper used by Style.use()
    # ------------------------------------------------------------ #
    def _run(self, params: LoadParamsT) -> ResultT:
        logger.debug("Starting LoadStyle '%s' Load.", self.style_name)
        result = self.load(params)
        logger.debug("LoadStyle '%s' Load completed.", self.style_name)
        return result


# ---------------------------------------------------------------------- #
# Excel Load
# ---------------------------------------------------------------------- #
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


LOAD_STYLE_CLASSES: Dict[str, type[LoadStyle[LoadParams, Any]]] = {
    "excel": ExcelLoadStyle,
}
