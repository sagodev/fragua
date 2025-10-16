"""
Base ExtractionStyle class for Fragua Miners.
Contains common utilities for extraction workflows.
"""

from abc import abstractmethod
from typing import Any, Generator
from datetime import datetime, UTC
from core.base_style import Style
from utils.logger import get_logger

logger = get_logger(__name__)

EXTRACTIONSTYLE_REGISTRY: dict[str, type] = {}


def register_extraction_style(name: str):
    def wrapper(cls):
        EXTRACTIONSTYLE_REGISTRY[name] = cls
        logger.debug("Registered ExtractionStyle: %s", name)
        return cls

    return wrapper


class ExtractionStyle(Style):
    """
    Base class for all extraction styles in Fragua ETL.
    """

    def __init__(self, style_name: str):
        super().__init__(style_name)
        self.created_at = datetime.now(UTC)

    @abstractmethod
    def extract(self, source: Any) -> Generator | Any:
        """Extract data from the given source."""

    def use(self, data: Any) -> Any:
        """
        Main transformation method.
        Executes forge -> validate -> postprocess pipeline.
        """
        if data is None:
            raise ValueError("Input data cannot be None")

        logger.debug(
            "Starting ForgeStyle '%s' transformation pipeline.", self.style_name
        )

        try:
            data = self.extract(data)
            logger.debug("%s: forge() step completed.", self.style_name)

            data = self.validate(data)
            logger.debug("%s: validate() step completed.", self.style_name)

            data = self.postprocess(data)
            logger.debug("%s: postprocess() step completed.", self.style_name)

            return data

        except Exception as e:
            self.log_error(e)
            raise
