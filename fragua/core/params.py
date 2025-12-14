"""
Base abstract class for all parameter schemas used by styles in Fragua.
"""

from abc import abstractmethod
from typing import Any, Dict, TypeVar
from fragua.core.component import FraguaComponent
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class FraguaParams(FraguaComponent):
    """
    Abstract base class for all parameter schemas used by Fragua styles.

    FraguaParams defines the configuration contract required by styles
    during ETL execution. Each concrete Params implementation represents
    a validated, self-describing configuration object associated with
    a specific action and style.

    Params objects are responsible for encapsulating configuration
    values, providing structured summaries, and exposing field-level
    descriptions for documentation and introspection.
    """

    FIELD_DESCRIPTIONS: dict[str, str] = {}

    def __init__(self, action: str, style: str) -> None:
        """
        Initialize the Params schema with an action and style.

        Args:
            action: ETL action scope where the params are applicable
                (e.g., "extract", "transform", "load").
            style: Style identifier associated with these parameters
                (e.g., "csv", "excel", "sql", "api").
        """
        super().__init__(component_name=self.__class__.__name__)
        self.action = action
        self.style = style

    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of the parameter configuration.

        Implementations should return serializable configuration data
        only and may leverage FIELD_DESCRIPTIONS to provide human-readable
        context for each parameter.

        Returns:
            A dictionary representing the parameter summary.
        """

    def __repr__(self) -> str:
        """
        Return a concise string representation of the Params instance.

        Returns:
            A string identifying the Params class, action, and style.
        """
        return f"{self.__class__.__name__}(role='{self.action}', style='{self.style}')"


FraguaParamsT = TypeVar("FraguaParamsT", bound=FraguaParams)
