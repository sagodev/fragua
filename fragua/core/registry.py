"""Fragua registry Class."""

from __future__ import annotations
from typing import Callable, Dict, Optional, List

from fragua.core.set import FraguaSet


class FraguaRegistry:
    """
    Runtime function registry.

    A FraguaRegistry stores named FraguaSet instances and
    resolves functions by set and function name.
    """

    _sets: Dict[str, FraguaSet]

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
        self._sets = sets or {}

    def create_set(self, name: str, *, step_enabled: bool = True) -> FraguaSet:
        """
        Create a new registry set.

        Args:
            name: Name of the set to create.
            step_enabled: Whether steps can be created from this set.
        """
        if self.get_set(name) is not None:
            raise ValueError(f"Registry set already exists: {name}")

        new_set = FraguaSet(name=name, step_enabled=step_enabled)

        return new_set

    def add_set(self, set_: FraguaSet) -> bool:
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

    def delete_set(self, name: str) -> bool:
        """
        Remove a function set from the registry.

        Returns True if the set was removed,
        False if no set with the given name exists.
        """
        if name not in self._sets:
            return False

        del self._sets[name]
        return True

    def get_set(self, name: str) -> Optional[FraguaSet]:
        """Retrieve a set by name."""
        return self._sets.get(name)

    def get_function(
        self, set_name: str, function_name: str
    ) -> Optional[Callable[..., object]]:
        """
        Resolve a function from a given set.

        Returns None if the set or function does not exist.
        """
        set_: Optional[FraguaSet] = self._sets.get(set_name)
        if not set_:
            return None

        return set_.get_function(function_name)

    def list_sets(self) -> List[str]:
        """Return the list of registered set names."""
        return list(self._sets.keys())
