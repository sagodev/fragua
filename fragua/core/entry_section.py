"""Entry section class."""

from typing import Any, Dict
from fragua.core.component import FraguaComponent


class EntrySection:
    """Wrapper that represents a single entry inside a SectionRegistry."""

    def __init__(self, name: str, component: FraguaComponent) -> None:
        """Initialize entry wrapper."""
        self._name = name
        self._component = component

    # ---------------------------------------------------------
    # Properties
    # ---------------------------------------------------------

    @property
    def summary(self) -> Dict[str, Any]:
        """Retrieve component summary."""
        return {
            "name": self._name,
            "component": self._component.summary(),
        }

    @property
    def name(self) -> str:
        """Retrieve entry name."""
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        """Set entry name."""
        self._name = new_name

    @property
    def component(self) -> FraguaComponent:
        """Retrieve component instance."""
        return self._component

    @component.setter
    def component(self, new_component: FraguaComponent) -> None:
        """Replace component instance."""
        self._component = new_component
