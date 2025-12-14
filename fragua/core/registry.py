"""Base class for all registries of an environment in Fragua."""

from typing import Dict, Optional

from fragua.core.component import FraguaComponent
from fragua.core.set import FraguaSet


class FraguaRegistry(FraguaComponent):
    """
    Base class for all registries within a Fragua environment.

    A FraguaRegistry manages a collection of FraguaSet instances,
    each representing a logical grouping of related components
    (such as styles, params, or functions) under a specific scope.

    Registries provide controlled creation, retrieval, update,
    and deletion of sets, and act as the backbone for dynamic
    component resolution within the environment.
    """

    def __init__(self, registry_name: str) -> None:
        """
        Initialize the registry with a name.

        Args:
            registry_name: Identifier used to reference this registry
                within the environment.
        """
        super().__init__(component_name=registry_name)
        self._set: Dict[str, FraguaSet] = {}

    def _exists(self, key: str) -> bool:
        """
        Check whether a registry set exists.

        Args:
            key: Name of the registry set.

        Returns:
            True if the set exists, False otherwise.
        """
        return key in self._set

    def _not_exists(self, key: str) -> bool:
        """
        Check whether a registry set does not exist.

        Args:
            key: Name of the registry set.

        Returns:
            True if the set does not exist, False otherwise.
        """
        return key not in self._set

    def get_sets(self) -> Dict[str, FraguaSet]:
        """
        Retrieve all registered sets.

        Returns:
            A dictionary mapping set names to FraguaSet instances.
        """
        return self._set

    def create_set(self, name: str, registry_set: FraguaSet) -> bool:
        """
        Register a new FraguaSet in the registry.

        Args:
            name: Name under which the set will be registered.
            registry_set: FraguaSet instance to register.

        Returns:
            True if the set was created successfully, False if a
            set with the same name already exists.
        """
        if self._not_exists(name):
            self._set[name] = registry_set
            return True
        return False

    def get_set(self, name: str) -> Optional[FraguaSet]:
        """
        Retrieve a registry set by name.

        Args:
            name: Name of the registry set.

        Returns:
            The FraguaSet instance if found, otherwise None.
        """
        return self._set.get(name)

    def update_set(self, old_name: str, new_name: str) -> bool:
        """
        Rename an existing registry set.

        Args:
            old_name: Current name of the registry set.
            new_name: New name to assign to the registry set.

        Returns:
            True if the set was renamed successfully, False if the
            old name does not exist or the new name is already taken.
        """
        if self._exists(old_name) and self._not_exists(new_name):
            self._set[new_name] = self._set.pop(old_name)
            return True
        return False

    def delete_set(self, name: str) -> bool:
        """
        Remove a registry set from the registry.

        Args:
            name: Name of the registry set to delete.

        Returns:
            True if the set was deleted, False if it did not exist.
        """
        return self._set.pop(name, None) is not None

    # ---------------------------------------------------------

    def __repr__(self) -> str:
        """
        Return a concise string representation of the registry.

        Returns:
            A string identifying the registry class and name.
        """
        return f"{self.__class__.__name__}('{self.name}')"
