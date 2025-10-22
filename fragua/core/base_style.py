"""
Base class for all styles used by ETL agents in Fragua.
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, Dict
from fragua.utils.logger import get_logger
from fragua.core.base_params import BaseParams

logger = get_logger(__name__)

# ---------------------------------------------------------------------- #
# Type Variables
# ---------------------------------------------------------------------- #
ResultT = TypeVar("ResultT")  # Output type (e.g., DataFrame, str, etc.)
ParamsT = TypeVar("ParamsT", bound=BaseParams)  # Must inherit from BaseParams


class BaseStyle(ABC, Generic[ParamsT, ResultT]):
    """
    Abstract base class for all styles in Fragua.
    Defines a standard interface for style operations.

    Each concrete Style defines its own Params subclass,
    e.g. DeliveryStyle uses DeliveryParams, ExtractionStyle uses ExtractionParams, etc.
    """

    def __init__(self, style_name: str):
        """Initialize the style with a given name."""
        self.style_name = style_name
        self.metadata: Dict[str, Any] = {}

    # ---------------------------------------------------------------------- #
    # Abstract Core
    # ---------------------------------------------------------------------- #

    @abstractmethod
    def use(self, params: ParamsT) -> ResultT:
        """
        Apply the style to the given input parameters.

        Args:
            params (ParamsT): Configuration or data to process.
        Returns:
            ResultT: The processed or delivered result.
        """

    # ---------------------------------------------------------------------- #
    # Validation hooks
    # ---------------------------------------------------------------------- #

    def validate_params(self, params: ParamsT) -> ParamsT:
        """
        Validate input parameters before execution.

        Args:
            params (ParamsT): Input configuration or data.
        Returns:
            ParamsT: Validated parameters.
        Raises:
            ValueError: If params is None or invalid.
        """
        if params is None:
            raise ValueError(f"{self.style_name}: Parameters cannot be None.")
        return params

    def validate_result(self, result: ResultT) -> ResultT:
        """
        Validate the result after execution.

        Args:
            result (ResultT): The result object.
        Returns:
            ResultT: Validated result.
        Raises:
            ValueError: If result is None or invalid.
        """
        if result is None:
            raise ValueError(f"{self.style_name}: Result cannot be None.")
        return result

    # ---------------------------------------------------------------------- #
    # Optional hooks
    # ---------------------------------------------------------------------- #

    def postprocess(self, result: ResultT) -> ResultT:
        """Optional postprocessing step after validation."""
        return result

    def log_error(self, error: Exception) -> None:
        """Log an error with the style context."""
        logger.error(
            "[%s ERROR] %s: %s", self.__class__.__name__, type(error).__name__, error
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} style_name={self.style_name}>"
