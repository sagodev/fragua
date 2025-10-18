"""
Base class for all styles used by ETL agents in Fragua.

Examples of styles include Forge Styles, Extraction Styles, and Delivery Styles.
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, Dict, Optional
from fragua.utils.logger import get_logger

logger = get_logger(__name__)

# Generic type variable for the result of style operations
ResultT = TypeVar("ResultT")
DataT = TypeVar("DataT")


class Style(ABC, Generic[DataT, ResultT]):
    """
    Abstract base class for style.

    Type Parameters:
        DataT: Type of input data the style accepts
        ResultT: Type of result the style produces
    """

    def __init__(self, style_name: str):
        """
        Initialize the style with a given name.

        Args:
            style_name (str): Name of the style.
        """
        self.style_name = style_name
        self.metadata: Dict[str, Any] = {}

    @abstractmethod
    def use(self, data: DataT) -> ResultT:
        """
        Apply the style to the given data.

        Args:
            data (DataT): Input data to be processed or transformed.

        Returns:
            ResultT: The processed/transformed result.

        Raises:
            ValueError: If data is None or invalid
            TypeError: If data is of wrong type
        """
        pass

    def validate(self, data: DataT) -> DataT:
        """
        Basic validation of the data.

        Args:
            data (DataT): Data to validate

        Returns:
            DataT: The validated data

        Raises:
            ValueError: If data is None
        """
        if data is None:
            raise ValueError("No data extracted")
        return data

    def postprocess(self, data: ResultT) -> ResultT:
        """
        Optional step for cleaning or formatting data.

        Args:
            data (ResultT): Data to postprocess

        Returns:
            ResultT: The postprocessed data
        """
        return data

    def log_error(self, error: Exception) -> None:
        """
        Basic error logging.

        Args:
            error (Exception): The error to log
        """
        logger.error(
            "[%s ERROR] %s: %s", self.__class__.__name__, type(error).__name__, error
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} style_name={self.style_name}>"
