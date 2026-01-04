"""Fragua registry.

Defines a lightweight registry that indexes function sets
and provides function resolution at runtime.
"""

from typing import Callable, Dict, Optional

import pandas as pd

from fragua.core.set import FraguaSet


class FraguaRegistry:
    """
    Runtime function registry.

    A FraguaRegistry stores named FraguaSet instances and
    resolves functions by set and function name.
    """

    def __init__(
        self,
        *,
        sets: Optional[Dict[str, FraguaSet]] = None,
    ) -> None:
        """
        Initialize the registry.

        Parameters
        ----------
        sets:
            Optional preloaded mapping of set name to FraguaSet.
        """
        self._sets: Dict[str, FraguaSet] = sets or {}

    def register_set(self, set_: FraguaSet) -> bool:
        """
        Register a function set.

        Returns True if the set was registered,
        False if a set with the same name already exists.
        """
        if set_.name in self._sets:
            return False

        self._sets[set_.name] = set_
        return True

    def replace_set(self, set_: FraguaSet) -> bool:
        """
        Replace an existing function set with a new one.

        Returns True if the set was replaced,
        False if no set with the same name exists.
        """
        if set_.name not in self._sets:
            return False

        self._sets[set_.name] = set_
        return True

    def get_set(self, name: str) -> Optional[FraguaSet]:
        """Retrieve a set by name."""
        return self._sets.get(name)

    def get_function(
        self, set_name: str, function_name: str
    ) -> Optional[Callable[..., pd.DataFrame]]:
        """
        Resolve a function from a given set.

        Returns None if the set or function does not exist.
        """
        set_ = self._sets.get(set_name)
        if not set_:
            return None

        return set_.get_function(function_name)

    def list_sets(self) -> list[str]:
        """Return the list of registered set names."""
        return list(self._sets.keys())
