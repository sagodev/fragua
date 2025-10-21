"""
Base class for all styles used by ETL agents in Fragua.
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, Dict
from fragua.utils.logger import get_logger
from fragua.core.base_params import BaseParams

logger = get_logger(__name__)

# Generics
ResultT = TypeVar("ResultT")
ParamsT = TypeVar("ParamsT", bound=BaseParams)


class BaseStyle(ABC, Generic[ParamsT, ResultT]):
    """
    Abstract base class for all styles using strong typing with BaseParams.

    Type Parameters:
        ParamsT: Subclass of BaseParams defining the input configuration.
        ResultT: Type of the result produced.
    """

    def __init__(self, style_name: str):
        self.style_name = style_name
        self.metadata: Dict[str, Any] = {}

    @abstractmethod
    def extract(self, source_params: ParamsT) -> ResultT:
        """
        Subclasses implement this method to extract/transform data.

        Args:
            source_params (ParamsT): Configuration or input data.

        Returns:
            ResultT: Processed or extracted data.
        """
        raise NotImplementedError

    def use(self, source_params: ParamsT) -> ResultT:
        """
        Main pipeline: extract -> validate -> postprocess.

        Args:
            source_params (ParamsT): Input configuration

        Returns:
            ResultT: Final processed result
        """
        if source_params is None:
            raise ValueError("source_params cannot be None")

        logger.debug("Starting '%s' style pipeline.", self.style_name)

        try:
            result: ResultT = self.extract(source_params)
            logger.debug("%s: extract() completed.", self.style_name)

            result = self.validate(result)
            logger.debug("%s: validate() completed.", self.style_name)

            result = self.postprocess(result)
            logger.debug("%s: postprocess() completed.", self.style_name)

            self.metadata.update(
                {
                    "last_used": result,
                    "params_type": type(source_params).__name__,
                    "result_type": (
                        type(result).__name__ if result is not None else None
                    ),
                }
            )

            return result
        except Exception as e:
            self.log_error(e)
            raise

    def validate(self, data: ResultT) -> ResultT:
        """Validates the extracted data. Raises error if invalid."""
        if data is None:
            raise ValueError("No data extracted")
        return data

    def postprocess(self, data: ResultT) -> ResultT:
        """Hook for subclasses to override for post-processing."""
        return data

    def log_error(self, error: Exception) -> None:
        """Logs errors that occur during the style pipeline."""
        logger.error(
            "[%s ERROR] %s: %s", self.__class__.__name__, type(error).__name__, error
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} style_name={self.style_name}>"
