"""Fragua set container.

Defines a minimal container for registering and retrieving
ETL functions and declarative pipelines at runtime.
"""

from typing import Any, Callable, Dict, Optional, Union


FraguaItem = Union[
    Callable[..., object],
    Dict[str, Any],  # Declarative pipeline definition
]


class FraguaSet:
    """
    Generic container for Fragua executable definitions.

    A FraguaSet stores named callables and/or declarative pipeline
    definitions and provides simple registration and lookup utilities.

    The set can be configured to expose or not its callables
    as FraguaStepBuilder templates.
    """

    def __init__(
        self,
        name: str,
        *,
        items: Optional[Dict[str, FraguaItem]] = None,
        step_enabled: bool = True,
    ) -> None:
        self.name = name
        self.step_enabled = step_enabled
        self._items: Dict[str, FraguaItem] = items or {}

    # -------------------------
    # Generic operations
    # -------------------------

    def exists(self, name: str) -> bool:
        """Return True if an item is registered under the given name."""
        return name in self._items

    def register(self, name: str, item: FraguaItem) -> bool:
        """
        Register a callable or declarative pipeline.

        Returns True if the item was registered,
        False if the name already exists.
        """
        if name in self._items:
            return False

        self._items[name] = item
        return True

    def get(self, name: str) -> Optional[FraguaItem]:
        """Retrieve an item by name."""
        return self._items.get(name)

    def remove(self, name: str) -> bool:
        """Remove an item from the set."""
        return self._items.pop(name, None) is not None

    def list(self) -> list[str]:
        """Return the list of registered item names."""
        return list(self._items.keys())

    # -------------------------
    # Typed accessors
    # -------------------------

    def get_function(
        self,
        name: str,
    ) -> Optional[Callable[..., object]]:
        """Retrieve a callable item. If not exist return None."""
        item = self.get(name)
        return item if callable(item) else None

    def get_pipeline_def(
        self,
        name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a definition of an pipeline item that is an dict.
        If not exist return None.
        """
        item = self.get(name)
        return item if isinstance(item, dict) else None
