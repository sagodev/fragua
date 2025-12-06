"""Component abstract class."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class FraguaComponent(ABC):
    """Fragua component abstract class."""

    def __init__(self, component_name: str):
        """Initialize component."""
        self.name = component_name

    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        """Return a structured summary of this component."""
