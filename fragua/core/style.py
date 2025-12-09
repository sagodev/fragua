"""
Base class for all styles used by ETL agents in Fragua.
"""

from abc import abstractmethod
from typing import TypeVar, Generic, Dict, Any
from fragua.core.component import FraguaComponent
from fragua.utils.logger import get_logger
from fragua.core.params import ParamsT

logger = get_logger(__name__)

ResultT = TypeVar("ResultT")


class Style(FraguaComponent, Generic[ParamsT, ResultT]):
    """
    Abstract base class for all styles in Fragua.
    Defines a standard interface for style operations.
    """

    def __init__(self):
        super().__init__(component_name=self.__class__.__name__)

    @abstractmethod
    def _run(self, params: ParamsT) -> ResultT:
        raise NotImplementedError

    def log_error(self, error: Exception) -> None:
        """log error funciton"""
        logger.error(
            "[%s ERROR] %s: %s", self.__class__.__name__, type(error).__name__, error
        )

    def use(self, params: ParamsT) -> ResultT:
        """Pipeline for style classes."""
        try:
            return self._run(params)
        except Exception as e:
            self.log_error(e)
            raise

    def summary(self) -> Dict[str, Any]:
        """Base style class summary."""

        return {
            "type": "style",
            "name": self.__class__.__name__,
            "fields": self.summary_fields(),
        }

    @abstractmethod
    def summary_fields(self) -> Dict[str, Any]:
        """
        Subclasses must return a dictionary describing:
        - purpose
        - internal functions/pipelines
        - expected params
        - behaviour
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} style_name={self.name}>"
