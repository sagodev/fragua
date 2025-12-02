"""Base class for all registries of an environment in Fragua."""

from typing import Any, Dict, Optional


class Registry:
    """Configuration class for all registries types of an environment."""

    def __init__(
        self, name: str, entries: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> None:
        """Initialize the registry."""
        self.name: str = name
        self._entries: Dict[str, Dict[str, Any]] = {} if entries is None else entries

    def _check_entrie_name(self, name: str) -> bool:
        """Ensure no entrie in the registry already has the given name."""
        return not any(name in entries for entries in self._entries.values())

    def set_entries(self, entries: Dict[str, Dict[str, Any]]) -> None:
        """Set or replace all registry entries."""
        self._entries = entries

    def get_entries(self) -> Dict[str, Dict[str, Any]]:
        """Retrive all registry entries."""
        return self._entries

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}')"
