"""Fragua set container.

Defines a minimal container for registering and retrieving
ETL functions and pipelines at runtime.
"""

from typing import Callable, Dict, Optional, Union

import pandas as pd

from fragua.core.pipeline import FraguaPipeline

FraguaItem = Union[Callable[..., pd.DataFrame], FraguaPipeline]


class FraguaSet:
    """
    Generic container for Fragua executable items.

    A FraguaSet stores named callables and/or pipelines and
    provides simple registration and lookup utilities.

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
        """
        Initialize the set.

        Parameters
        ----------
        name:
            Identifier of the set within a registry.
        items:
            Optional preloaded functions or pipelines.
        step_enabled:
            Whether callables registered in this set should
            automatically generate FraguaStepBuilder templates.
        """
        self.name = name
        self.step_enabled = step_enabled
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
        """Retrieve a FraguaPipeline item. If not exist return None."""
        item = self.get(name)
        return item if isinstance(item, FraguaPipeline) else None

    def get_function(self, name: str) -> Optional[Callable[..., pd.DataFrame]]:
        """Retrieve a callable item. If not exist return None."""
        item = self.get(name)
        return item if callable(item) else None

    def remove(self, name: str) -> bool:
        """Remove an item from the set."""
        return self._items.pop(name, None) is not None

    def list(self) -> list[str]:
        """Return the list of registered item names."""
        return list(self._items.keys())
