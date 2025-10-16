"""
Base ExtractionStyle class for Fragua Miners.
Contains common utilities for extraction workflows.
"""

from abc import ABC, abstractmethod
from typing import Any, Generator
from datetime import datetime, UTC

from utils.logger import get_logger

# Unified logger for ExtractionStyle
logger = get_logger(__name__)

# Registry for dynamic ExtractionStyle discovery
EXTRACTIONSTYLE_REGISTRY: dict[str, type] = {}


def register_extraction_style(name: str):
    """
    Decorator to register an ExtractionStyle subclass dynamically.
    """

    def wrapper(cls):
        EXTRACTIONSTYLE_REGISTRY[name] = cls
        logger.debug("Registered ExtractionStyle: %s", name)
        return cls

    return wrapper


class ExtractionStyle(ABC):
    """
    Base class for all extraction styles in Fragua ETL.

    Defines the lifecycle of data extraction:
    - extract: obtain data from a source
    - validate: ensure data integrity
    - postprocess: optional cleanup or formatting
    """

    def __init__(self, style_name: str):
        if not style_name or not isinstance(style_name, str):
            raise ValueError("style_name must be a non-empty string")
        self.style_name = style_name
        self.created_at = datetime.now(UTC)

    def use(self, source: Any) -> Any:
        """
        Execute the full extraction workflow.
        Handles errors, validation, and optional postprocessing.
        """
        try:
            logger.debug(
                "[%s] Using extraction style on source: %s", self.style_name, source
            )
            data = self.extract(source)
            validated = self.validate(data)
            result = self.postprocess(validated)
            logger.debug("[%s] Extraction completed successfully.", self.style_name)
            return result
        except Exception as e:
            self.log_error(e)
            raise

    @abstractmethod
    def extract(self, source: Any) -> Generator | Any:
        """Extract data from the given source."""
        pass

    def validate(self, data: Any) -> Any:
        """Performs a basic validation of the extracted data."""
        if data is None:
            raise ValueError("No data extracted")
        return data

    def postprocess(self, data: Any) -> Any:
        """Optional data cleanup or transformation step."""
        return data

    def log_error(self, error: Exception) -> None:
        """Handles error reporting."""
        logger.error(
            "[%s] ExtractionStyle ERROR: %s: %s",
            self.style_name,
            type(error).__name__,
            error,
        )

    def __repr__(self):
        return f"<{self.__class__.__name__} style_name={self.style_name}>"
