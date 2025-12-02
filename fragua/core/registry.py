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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}')"
