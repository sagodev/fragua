"""
Base class for all styles used by ETL agents in Fragua.
"""

from abc import ABC, abstractmethod
from typing import Generic, Dict, Any, Optional, TypeVar

from fragua.core.component import FraguaComponent
from fragua.utils.logger import get_logger
from fragua.core.params import FraguaParamsT

logger = get_logger(__name__)


class FraguaStyle(FraguaComponent, ABC, Generic[FraguaParamsT]):
    """
    Base abstract class for all styles in Fragua.

    Subclasses must implement `execute` and can define `fields` as metadata.
    """

    action: str
    function: str
    params_type: str
    purpose: str | None = None

    def __init__(self, style_name: Optional[str] = None):
        super().__init__(component_name=style_name or self.__class__.__name__)

    @abstractmethod
    def execute(self, params: FraguaParamsT) -> Any:
        """
        Execute the style logic.

        Args:
            params: Parameters required by the style.

        Returns:
            The processed data.
        """
        raise NotImplementedError

    def summary_fields(self) -> Dict[str, Any]:
        """
        Return a structured summary of the style, including fields.
        """
        return {
            "style_name": self.__class__.__name__,
            "purpose": self.purpose,
            "action": self.action,
            "function": self.function,
            "parameters_type": self.params_type,
        }

    def summary(self) -> Dict[str, Any]:
        """
        Generate a structured summary describing the style.

        The summary includes the style type, name, and detailed
        field-level information provided by the concrete implementation.

        Returns:
            A dictionary representing the style summary.
        """
        return {
            "type": "style",
            "name": self.__class__.__name__,
            "fields": self.summary_fields(),
        }


FraguaStyleT = TypeVar("FraguaStyleT", bound=FraguaStyle)
