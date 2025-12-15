"""Fragua Set class."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from fragua.core.component import FraguaComponent


class FraguaSet(ABC):
    """
    Abstract base class representing a logical set of Fragua components.

    A FraguaSet groups related FraguaComponent instances under a common
    scope (such as styles, params, or functions). Sets provide controlled
    lifecycle management for components and expose structured summaries
    for introspection and registry-level reporting.
    """

    def __init__(
        self,
        set_name: str,
        components: Optional[Dict[str, FraguaComponent]] = None,
    ):
        """
        Initialize the set with a name and optional preloaded components.

        Args:
            set_name: Identifier of the set within its parent registry.
            components: Optional dictionary of pre-registered components.
        """
        self.set_name = set_name
        self._components: Dict[str, FraguaComponent] = (
            {} if components is None else components
        )

    def _exists(self, key: str) -> bool:
        """
        Check whether a component exists in the set.

        Args:
            key: Component name.

        Returns:
            True if the component exists, False otherwise.
        """
        return key in self._components

    def _not_exists(self, key: str) -> bool:
        """
        Check whether a component does not exist in the set.

        Args:
            key: Component name.

        Returns:
            True if the component does not exist, False otherwise.
        """
        return key not in self._components

    def add(self, name: str, component: FraguaComponent) -> bool:
        """
        Add a new component to the set.

        Args:
            name: Name under which the component will be registered.
            component: FraguaComponent instance to add.

        Returns:
            True if the component was added successfully, False if a
            component with the same name already exists.
        """
        if self._not_exists(name):
            self._components[name] = component
            return True
        return False

    def get_one(self, name: str) -> Optional[FraguaComponent]:
        """
        Retrieve a single component by name.

        Args:
            name: Name of the component.

        Returns:
            The FraguaComponent instance if found, otherwise None.
        """
        return self._components.get(name)

    def get_all(self) -> Dict[str, FraguaComponent]:
        """
        Retrieve all components in the set.

        Returns:
            A dictionary mapping component names to FraguaComponent instances.
        """
        return self._components

    def update(self, old_name: str, new_name: str) -> bool:
        """
        Rename a component within the set.

        Args:
            old_name: Current component name.
            new_name: New component name.

        Returns:
            True if the component was renamed successfully, False if the
            old name does not exist or the new name is already in use.
        """
        if self._exists(old_name) and self._not_exists(new_name):
            component = self._components.pop(old_name)
            self._components[new_name] = component
            return True
        return False

    def delete_one(self, name: str) -> bool:
        """
        Remove a component from the set.

        Args:
            name: Name of the component to delete.

        Returns:
            True if the component was removed, False if it did not exist.
        """
        return self._components.pop(name, None) is not None

    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of the set contents.

        Implementations should aggregate component summaries and expose
        metadata relevant to the specific set type.

        Returns:
            A dictionary representing the set summary.
        """
