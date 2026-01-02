"""Fragua function set.

Defines a minimal container for registering and retrieving
callable ETL functions at runtime.
"""

from typing import Callable, Dict, Optional


class FraguaSet:
    """
    Container for ETL functions.

    A FraguaSet stores named callables and provides
    simple registration and lookup utilities.
    """

    def __init__(
        self,
        name: str,
        *,
        functions: Optional[Dict[str, Callable]] = None,
    ) -> None:
        """
        Initialize the function set.

        Parameters
        ----------
        name:
            Identifier of the set within a registry.
        functions:
            Optional preloaded functions.
        """
        self.name = name
        self._functions: Dict[str, Callable] = functions or {}

    def exists(self, name: str) -> bool:
        """Return True if a function is registered under the given name."""
        return name in self._functions

    def register(self, name: str, fn: Callable) -> bool:
        """
        Register a function in the set.

        Returns True if the function was registered,
        False if the name already exists.
        """
        if name in self._functions:
            return False

        self._functions[name] = fn
        return True

    def get(self, name: str) -> Optional[Callable]:
        """Retrieve a function by name."""
        return self._functions.get(name)

    def remove(self, name: str) -> bool:
        """Remove a function from the set."""
        return self._functions.pop(name, None) is not None

    def list(self) -> list[str]:
        """Return the list of registered function names."""
        return list(self._functions.keys())
