"""Base class for all registries of an environment in Fragua."""

from typing import Dict, Optional

from fragua.core.component import FraguaComponent
from fragua.core.set import FraguaSet


class FraguaRegistry(FraguaComponent):
    """
    Fragua registry class.
    This class handle management for fragua sets.
    """

    def __init__(self, registry_name: str) -> None:
        """Initialize the registry."""
        super().__init__(component_name=registry_name)
        self._set: Dict[str, FraguaSet] = {}

    def _exists(self, key: str) -> bool:
        """Return True if the registry set exists."""
        return key in self._set

    def _not_exists(self, key: str) -> bool:
        """Return True if the registry set does not exist."""
        return key not in self._set

    def get_sets(self) -> Dict[str, FraguaSet]:
        """Retrieve all registered sections."""
        return self._set

    def create_set(self, name: str, registry_set: FraguaSet) -> bool:
        """Create a new registry set."""
        if self._not_exists(name):
            self._set[name] = registry_set
            return True
        return False

    def get_set(self, name: str) -> Optional[FraguaSet]:
        """Retrieve a registry set by name."""
        return self._set.get(name)

    def update_set(self, old_name: str, new_name: str) -> bool:
        """Rename a registry set."""
        if self._exists(old_name) and self._not_exists(new_name):
            self._set[new_name] = self._set.pop(old_name)
            return True
        return False

    def delete_set(self, name: str) -> bool:
        """Delete a registry set."""
        return self._set.pop(name, None) is not None

    # ---------------------------------------------------------

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"
