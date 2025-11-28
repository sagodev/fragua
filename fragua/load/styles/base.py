"""Base Load Style Class."""

from abc import abstractmethod

from typing import Any, Dict, Generic
from fragua.core.style import ResultT, Style
from fragua.load.params.generic_types import LoadParamsT

from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class LoadStyle(Style[LoadParamsT, ResultT], Generic[LoadParamsT, ResultT]):
    """
    Base class for all Load styles in Fragua ETL.

    Standard pipeline provided by Style:
        validate_params -> _run -> validate_result -> postprocess
    """

    def summary_fields(self) -> Dict[str, Any]:
        """
        Returns metadata describing this LoadStyle.
        Each subclass should extend or override.
        """
        return {
            "style_type": "load",
            "description": "Handles loading data into external destinations.",
        }

    @abstractmethod
    def load(self, params: LoadParamsT) -> ResultT:
        """
        Load the given data to the target destination.
        Must be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement load()")

    def _run(self, params: LoadParamsT) -> ResultT:
        logger.debug("Starting LoadStyle '%s' Load.", self.style_name)
        result = self.load(params)
        logger.debug("LoadStyle '%s' Load completed.", self.style_name)
        return result
