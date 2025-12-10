"""
Base abstract class for all parameter schemas used by styles in Fragua.
"""

from abc import abstractmethod
from typing import Any, Dict, TypeVar
from fragua.core.component import FraguaComponent
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Params(FraguaComponent):
    """
    Abstract base configuration class for all Fragua parameter types.

    Attributes:
        action (str): Defines the agent action such as "extract", "transform", or "load".
        style (str): Defines the style or data source type (e.g., "csv", "excel", "sql", "api").
    """

    FIELD_DESCRIPTIONS: dict[str, str] = {}

    def __init__(self, action: str, style: str) -> None:
        super().__init__(component_name=self.__class__.__name__)
        self.action = action
        self.style = style

    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        """Base params class summary."""

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(role='{self.action}', style='{self.style}')"


ParamsT = TypeVar("ParamsT", bound=Params)
