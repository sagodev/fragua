"""Section Registry class."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type

from fragua.core.component import FraguaComponent


class RegistrySet(ABC):
    """Section registry class."""

    def __init__(
        self,
        section_name: str,
        entries: Optional[Dict[str, Type[FraguaComponent]]] = None,
    ):
        """Initialize section registry."""
        self.section_name = section_name
        self._entries: Dict[str, Type[FraguaComponent]] = (
            {} if entries is None else entries
        )

    def _exists(self, key: str) -> bool:
        """Return True if the entry exists."""
        return key in self._entries

    def _not_exists(self, key: str) -> bool:
        """Return True if the entry does not exist."""
        return key not in self._entries

    def create_one(self, name: str, component: Type[FraguaComponent]) -> bool:
        """Create an entry linked to a component."""

        if self._not_exists(name):
            self._entries[name] = component
            return True
        return False

    def get_one(self, name: str) -> Optional[Type[FraguaComponent]]:
        """Retrieve a specific entry."""
        return self._entries.get(name)

    def get_all(self) -> Dict[str, Type[FraguaComponent]]:
        """Retrieve all entries."""
        return self._entries

    def update_one(self, old_name: str, new_name: str) -> bool:
        """Rename an entry."""
        if self._exists(old_name) and self._not_exists(new_name):
            entry = self._entries.pop(old_name)
            self._entries[new_name] = entry
            return True
        return False

    def delete_one(self, name: str) -> bool:
        """Delete an entry."""
        return self._entries.pop(name, None) is not None

    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        """Section registry summary."""
