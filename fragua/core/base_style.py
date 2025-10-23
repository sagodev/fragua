"""
Base class for all styles used by ETL agents in Fragua.
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, Dict
from datetime import datetime, timezone
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

    Metadata dictionary structure for all styles:
        - style_name: str, name of the style
        - style_type: Actual class name (e.g., 'ExcelMineStyle').
        - created_at: datetime, when the style instance was created
        - created_by: Optional[str], creator of the style
        - last_execution: Optional[datetime], last time the style was executed
        - params_type: Optional[str], type of parameters passed
        - result_type: Optional[str], type of result returned
    """

    def __init__(self, style_name: str, created_by: str | None = None):
        """Initialize the style with a given name and creator."""
        self.style_name = style_name
        self.metadata: Dict[str, Any] = {
            "style_name": style_name,
            "style_type": self.__class__.__name__,
            "created_at": datetime.now(timezone.utc),
            "created_by": created_by,
            "last_execution": None,
            "params_type": None,
            "result_type": None,
        }

    # ---------------------------------------------------------------------- #
    # Abstract Core
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def _run(self, params: ParamsT) -> ResultT:
        """
        Core implementation of the style.

        Must be implemented by subclasses:
        - MineStyle -> extract
        - ForgeStyle -> forge
        - DeliveryStyle -> deliver
        """
        raise NotImplementedError

    # ---------------------------------------------------------------------- #
    # Validation hooks
    # ---------------------------------------------------------------------- #
    def validate_params(self, params: ParamsT) -> ParamsT:
        """Validate input parameters before execution."""
        if params is None:
            raise ValueError(f"{self.style_name}: Parameters cannot be None.")
        return params

    def validate_result(self, result: ResultT) -> ResultT:
        """Validate the result after execution."""
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

    # ---------------------------------------------------------------------- #
    # Public pipeline
    # ---------------------------------------------------------------------- #
    def use(self, params: ParamsT) -> ResultT:
        """
        Execute the full style pipeline.

        Steps:
            1. validate_params
            2. _run (extract/forge/deliver)
            3. validate_result
            4. postprocess

        Updates standard metadata fields automatically.
        """
        try:
            self.validate_params(params)
            result = self._run(params)
            result = self.validate_result(result)
            result = self.postprocess(result)

            # Update metadata
            self.metadata.update(
                {
                    "last_execution": datetime.now(timezone.utc),
                    "params_type": type(params).__name__,
                    "result_type": (
                        type(result).__name__ if result is not None else None
                    ),
                }
            )

            return result

        except Exception as e:
            self.log_error(e)
            raise

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} style_name={self.style_name}>"
