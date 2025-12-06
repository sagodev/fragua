"""
Base abstract class for all parameter schemas used by styles in Fragua.
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Params(ABC):
    """
    Abstract base configuration class for all Fragua parameter types.

    Attributes:
        action (str): Defines the agent action such as "extract", "transform", or "load".
        style (str): Defines the style or data source type (e.g., "csv", "excel", "sql", "api").
    """

    FIELD_DESCRIPTIONS: dict[str, str] = {}
    purpose: str | None = None

    def __init__(self, action: str, style: str) -> None:
        self.action = action
        self.style = style

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(role='{self.action}', style='{self.style}')"

    @abstractmethod
    def summary(self) -> dict[str, Any]:
        """Return a structured summary of this Params object."""


ParamsT = TypeVar("ParamsT", bound=Params)
