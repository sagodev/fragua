"""Fragua Set class."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from fragua.core.component import FraguaComponent


class FraguaSet(ABC):
    """
    Fragua set class.
    This class handle management for fragua components.
    """

    def __init__(
        self,
        set_name: str,
        components: Optional[Dict[str, FraguaComponent]] = None,
    ):
        """Initialize set."""
        self.set_name = set_name
        self._components: Dict[str, FraguaComponent] = (
            {} if components is None else components
        )

    def _exists(self, key: str) -> bool:
        """Return True if the component exists."""
        return key in self._components

    def _not_exists(self, key: str) -> bool:
        """Return True if the component does not exist."""
        return key not in self._components

    def add(self, name: str, component: FraguaComponent) -> bool:
        """Add an new component."""

        if self._not_exists(name):
            self._components[name] = component
            return True
        return False

    def get_one(self, name: str) -> Optional[FraguaComponent]:
        """Retrieve a specific component."""
        return self._components.get(name)

    def get_all(self) -> Dict[str, FraguaComponent]:
        """Retrieve all components."""
        return self._components

    def update(self, old_name: str, new_name: str) -> bool:
        """Rename an component."""
        if self._exists(old_name) and self._not_exists(new_name):
            component = self._components.pop(old_name)
            self._components[new_name] = component
            return True
        return False

    def delete_one(self, name: str) -> bool:
        """Delete an component."""
        return self._components.pop(name, None) is not None

    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        """Set summary."""
