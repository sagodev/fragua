"""Base class for all registries of an environment in Fragua."""

from typing import Any, Dict


class Registry:
    """Configuration class for all registries types of an environment."""

    def __init__(self, name: str, entries: Dict[str, Dict[str, Any]]) -> None:
        """Initialize the registry."""
        self.name = name
        self.entries = entries

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}')"
