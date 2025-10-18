"""
Base ExtractionStyle class for Fragua Miners.
Contains common utilities for extraction workflows.
"""

from abc import abstractmethod
from typing import Any, TypeVar, Dict, Union
from datetime import datetime, UTC
import pandas as pd
from core.base_style import Style
from agents.store.wagon import Wagon
from utils.logger import get_logger

logger = get_logger(__name__)

# Type for source data - could be file path, connection string, API endpoint, etc.
SourceT = TypeVar("SourceT")

# We know extracted data will always be DataFrame or list for Wagon
ExtractedDataT = Union[pd.DataFrame, list[Any]]


def register_extraction_style(name: str):
    """
    Decorator to register an ExtractionStyle subclass.

    Args:
        name (str): Name to register the style under

    Returns:
        callable: Class decorator function
    """

    def wrapper(
        cls: type["ExtractionStyle[Any, Any]"],
    ) -> type["ExtractionStyle[Any, Any]"]:
        EXTRACTIONSTYLE_REGISTRY[name] = cls
        logger.debug("Registered ExtractionStyle: %s", name)
        return cls

    return wrapper


class ExtractionStyle(Style[SourceT, Wagon]):
    """
    Base class for all extraction styles in Fragua ETL.

    Type Parameters:
        SourceT: Type of source data (e.g., str for paths, dict for connection params)
        ExtractedDataT: Type alias for DataFrame or list - valid Wagon data types
    """

    def __init__(self, style_name: str):
        super().__init__(style_name)
        self.created_at = datetime.now(UTC)
        self.metadata: Dict[str, Any] = {"created_at": self.created_at}

    @abstractmethod
    def extract(self, source: SourceT) -> ExtractedDataT:
        """
        Extract data from the given source.

        Args:
            source (SourceT): The source to extract data from

        Returns:
            ExtractedDataT: The extracted data as DataFrame or list

        Raises:
            ValueError: If source is invalid
            IOError: If extraction fails
        """
        raise NotImplementedError

    def use(self, data: SourceT) -> Wagon:
        """
        Main extraction method.
        Executes extract -> validate -> postprocess pipeline.

        Args:
            data (SourceT): Source to extract data from

        Returns:
            Wagon: Container with extracted and processed data

        Raises:
            ValueError: If data source is None or invalid
            TypeError: If postprocess returns non-Wagon
            Exception: If any step in the pipeline fails
        """
        if data is None:
            raise ValueError("Input source cannot be None")

        logger.debug(
            "Starting ExtractionStyle '%s' extraction pipeline.", self.style_name
        )

        try:
            # Extract phase
            extracted = self.extract(data)
            logger.debug("%s: extract() step completed.", self.style_name)

            # Convert generator to data if needed
            if isinstance(extracted, Generator):
                extracted = list(extracted)

            # Validate phase
            validated = self.validate(extracted)
            logger.debug("%s: validate() step completed.", self.style_name)

            # Create wagon and postprocess
            wagon = Wagon(name=self.style_name, data=validated)
            result = self.postprocess(wagon)
            logger.debug("%s: postprocess() step completed.", self.style_name)

            # Update metadata with operation details
            source_type = type(data).__name__
            result_type = (
                type(result.data).__name__
                if hasattr(result, "data") and result.data is not None
                else None
            )

            self.metadata.update(
                {
                    "last_extraction": datetime.now(UTC),
                    "source_type": source_type,
                    "result_type": result_type,
                }
            )

            return result

        except Exception as e:
            self.log_error(e)
            raise


# Registry for dynamic ExtractionStyle discovery
EXTRACTIONSTYLE_REGISTRY: Dict[str, type[ExtractionStyle[Any]]] = {}
