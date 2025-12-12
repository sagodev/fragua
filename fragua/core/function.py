"""
Base abstract class for all function schemas used by styles in Fragua.
"""

from abc import abstractmethod
from typing import Any

from fragua.core.component import FraguaComponent


class FraguaFunction(FraguaComponent):
    """
    Represents a generic Fragua function that defines a name,
    an action, and an associated Params instance.
    """

    def __init__(self, function_name: str, action: str) -> None:
        super().__init__(component_name=function_name)
        self.action: str = action

    @abstractmethod
    def execute(self) -> Any:
        """Executes the function's action. Should be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement the execute method.")
