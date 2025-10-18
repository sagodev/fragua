"""
Base ExtractionStyle class for Fragua Miners.
Contains common utilities for extraction workflows.
"""

from abc import abstractmethod
from typing import Any, Dict, Union, Generator
from datetime import datetime, UTC
import pandas as pd
from fragua.core.base_style import Style
from fragua.agents.store.wagon import Wagon
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


def register_extraction_style(name: str):
    """
    Decorator to register an ExtractionStyle subclass.

    Args:
        name (str): Name to register the style under

    Returns:
        callable: Class decorator function
    """

    def wrapper(cls: type["ExtractionStyle"]) -> type["ExtractionStyle"]:
        EXTRACTIONSTYLE_REGISTRY[name] = cls
        logger.debug("Registered ExtractionStyle: %s", name)
        return cls

    return wrapper


class ExtractionStyle(Style[Dict[str, Any], Wagon]):
    """Base class for all extraction styles in Fragua ETL.

    Extraction styles implement different methods to extract data from sources like CSV files,
    Excel files, databases, APIs etc. Each style takes its configuration parameters as a
    dictionary in the extract method, allowing more flexibility in how the configuration
    is provided.

    Example:
        class CSVExtractionStyle(ExtractionStyle):
            def extract(self, source_params: Dict[str, Any]) -> pd.DataFrame:
                path = source_params.get("path")
                read_kwargs = source_params.get("read_kwargs", {})
                return pd.read_csv(path, **read_kwargs)
    """

    def __init__(self, style_name: str):
        super().__init__(style_name)
        self.created_at = datetime.now(UTC)
        self.metadata: Dict[str, Any] = {"created_at": self.created_at}

    @abstractmethod
    def extract(self, source_params: Dict[str, Any]) -> Union[pd.DataFrame, list[Any]]:
        """Extract data according to source parameters.

        Args:
            source_params (Dict[str, Any]): Configuration parameters for the extraction
                Will vary by style but typically includes source location (file path,
                connection string, URL) and extraction options.

        Returns:
            Union[pd.DataFrame, list[Any]]: The extracted data as a DataFrame
                or list depending on the source and style.

        Raises:
            ValueError: If required parameters are missing or invalid
            IOError: If data cannot be extracted from source
        """
        raise NotImplementedError

    def use(
        self, source_params: Dict[str, Any]
    ) -> Wagon[Union[pd.DataFrame, list[Any]]]:
        """Main extraction pipeline method.

        Executes extract -> validate -> postprocess workflow.

        Args:
            source_params (Dict[str, Any]): Configuration for extracting data
                from source. Format varies by style.

        Returns:
            Wagon[Union[pd.DataFrame, list[Any]]]: Container with extracted
                and processed data.

        Raises:
            ValueError: If source_params is None or missing required fields
            TypeError: If postprocess returns invalid type
            Exception: If any pipeline step fails
        """
        if source_params is None:
            raise ValueError("Source parameters cannot be None")

        logger.debug(
            "Starting ExtractionStyle '%s' extraction pipeline.", self.style_name
        )

        try:
            # Extract phase
            extracted = self.extract(source_params)
            logger.debug("%s: extract() step completed.", self.style_name)

            # Convert generator to list if needed
            if isinstance(extracted, Generator):
                extracted = list(extracted)

            # Create wagon and update its data
            result = Wagon(name=self.style_name, data=extracted)

            # Update metadata
            self.metadata.update(
                {
                    "last_extraction": datetime.now(UTC),
                    "params_type": type(source_params).__name__,
                    "result_type": (
                        type(result.data).__name__ if result.data is not None else None
                    ),
                }
            )

            return result

        except Exception as e:
            self.log_error(e)
            raise


# Registry for dynamic style discovery
EXTRACTIONSTYLE_REGISTRY: Dict[str, type[ExtractionStyle]] = {}
