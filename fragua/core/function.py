"""
Base abstract class for all function schemas used by styles in Fragua.
"""

from abc import abstractmethod
from typing import Any, Generic, Dict

from fragua.core.component import FraguaComponent
from fragua.core.params import ParamsT


class FraguaFunction(FraguaComponent, Generic[ParamsT]):
    """
    Represents a generic Fragua function that defines a name,
    an action, and an associated Params instance.
    """

    purpose: str = ""

    def __init__(self, function_name: str, action: str, params: ParamsT) -> None:
        super().__init__(component_name=function_name)
        self.action: str = action
        self.params: ParamsT = params

    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        """Base function class summary."""

    @abstractmethod
    def execute(self) -> Any:
        """Executes the function's action. Should be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement the execute method.")
