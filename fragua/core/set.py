"""Fragua set container.

Defines a minimal container for registering and retrieving
ETL functions and pipelines at runtime.
"""

from typing import Dict, Optional, Union, Callable

import pandas as pd

from fragua.core.pipeline import FraguaPipeline

FraguaItem = Union[Callable, FraguaPipeline]


class FraguaSet:
    """
    Generic container for Fragua executable items.

    A FraguaSet stores named callables and/or pipelines and
    provides simple registration and lookup utilities.
    """

    def __init__(
        self,
        name: str,
        *,
        items: Optional[Dict[str, FraguaItem]] = None,
    ) -> None:
        """
        Initialize the set.

        Parameters
        ----------
        name:
            Identifier of the set within a registry.
        items:
            Optional preloaded functions or pipelines.
        """
        self.name = name
        self._items: Dict[str, FraguaItem] = items or {}

    def exists(self, name: str) -> bool:
        """Return True if an item is registered under the given name."""
        return name in self._items

    def register(self, name: str, item: FraguaItem) -> bool:
        """
        Register an item in the set.

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

    def get_pipeline(self, name: str) -> Optional[FraguaPipeline]:
        """Retrive an FraguaPipeline item. If not exist return None."""
        item = self.get(name)
        return item if isinstance(item, FraguaPipeline) else None

    def get_function(self, name: str) -> Optional[Callable[..., pd.DataFrame]]:
        """Retrive an Callable item. If not exist return None."""
        item = self.get(name)
        return item if callable(item) else None

    def remove(self, name: str) -> bool:
        """Remove an item from the set."""
        return self._items.pop(name, None) is not None

    def list(self) -> list[str]:
        """Return the list of registered item names."""
        return list(self._items.keys())
