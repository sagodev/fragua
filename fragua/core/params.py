"""
Base abstract class for all parameter schemas used by styles in Fragua.
"""

from abc import ABC
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

    def summary(self) -> dict[str, Any]:
        """Return a structured summary of this Params object."""
        fields = {}

        for name in self.__annotations__:
            desc = self.FIELD_DESCRIPTIONS.get(name, "No description available.")
            fields[name] = desc

        return {
            "name": self.__class__.__name__,
            "action": self.action,
            "style": self.style,
            "fields": fields,
            "purpose": getattr(self, "purpose", None),
        }


ParamsT = TypeVar("ParamsT", bound=Params)
