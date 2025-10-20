"""
Base ExtractionStyle class for Fragua Miners.
Contains common utilities for extraction workflows.
"""

from abc import abstractmethod
from typing import Any, Dict, Callable, Type, Generic
from datetime import datetime, timezone
from fragua.core.base_style import BaseStyle, DataT, ResultT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)

EXTRACTIONSTYLE_REGISTRY: Dict[str, Type["ExtractionStyle[Any, Any]"]] = {}


def register_extraction_style(
    name: str,
) -> Callable[
    [Type["ExtractionStyle[DataT, ResultT]"]], Type["ExtractionStyle[DataT, ResultT]"]
]:
    """
    Decorator to register an ExtractionStyle subclass.
    """

    def wrapper(
        cls: Type["ExtractionStyle[DataT, ResultT]"],
    ) -> Type["ExtractionStyle[DataT, ResultT]"]:
        EXTRACTIONSTYLE_REGISTRY[name] = cls
        logger.debug("Registered ExtractionStyle: %s", name)
        return cls

    return wrapper


class ExtractionStyle(BaseStyle[DataT, ResultT], Generic[DataT, ResultT]):
    """Base class for all extraction styles in Fragua ETL."""

    def __init__(self, style_name: str):
        super().__init__(style_name)
        self.created_at = datetime.now(timezone.utc)
        self.metadata: Dict[str, Any] = {"created_at": self.created_at}

    @abstractmethod
    def extract(self, source_params: DataT) -> ResultT:
        """
        Extract data according to source parameters.

        Args:
            source_params (DataT): Configuration for extraction

        Returns:
            ResultT: Extracted and processed data
        """
        raise NotImplementedError

    def use(self, source_params: DataT) -> ResultT:
        """Main extraction pipeline method."""
        if source_params is None:
            raise ValueError("Source parameters cannot be None")

        logger.debug(
            "Starting ExtractionStyle '%s' extraction pipeline.", self.style_name
        )

        try:
            result: ResultT = self.extract(source_params)
            logger.debug("%s: extract() step completed.", self.style_name)

            result = self.validate(result)
            logger.debug("%s: validate() step completed.", self.style_name)

            result = self.postprocess(result)
            logger.debug("%s: postprocess() step completed.", self.style_name)

            self.metadata.update(
                {
                    "last_extraction": datetime.now(timezone.utc),
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
