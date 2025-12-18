"""
Fragua Set class.
"""

from abc import ABC
from typing import Any, Dict, Generic, Optional, Type, TypeVar, cast

from fragua.core.component import FraguaComponent
from fragua.core.fragua_class import FraguaClass
from fragua.core.fragua_instance import FraguaInstance


T = TypeVar("T")


class FraguaSet(ABC, Generic[T]):
    """
    Abstract base class representing a logical set of Fragua elements.

    A FraguaSet groups related items under a common scope (such as
    params schemas, function factories, styles, or agent instances).
    The stored elements may be either concrete instances or classes,
    depending on the responsibility of the set.
    """

    def __init__(
        self,
        set_name: str,
        component_type: Type[T] = FraguaComponent,
        components: Optional[Dict[str, T]] = None,
    ) -> None:
        """
        Initialize the set with a name and optional preloaded elements.

        Args:
            set_name: Identifier of the set within its parent registry.
            components: Optional dictionary of pre-registered elements.
        """
        self.set_name = set_name
        self.component_type = component_type
        self._components: Dict[str, T] = {} if components is None else components

    def _exists(self, key: str) -> bool:
        """
        Check whether an element exists in the set.

        Args:
            key: Element name.

        Returns:
            True if the element exists, False otherwise.
        """
        return key in self._components

    def _not_exists(self, key: str) -> bool:
        """
        Check whether an element does not exist in the set.

        Args:
            key: Element name.

        Returns:
            True if the element does not exist, False otherwise.
        """
        return key not in self._components

    def add(self, name: str, component: T) -> bool:
        """
        Add a new element to the set.

        Args:
            name: Name under which the element will be registered.
            component: Element (instance or class) to add.

        Returns:
            True if the element was added successfully, False if a
            component with the same name already exists.
        """
        if self._not_exists(name):
            self._components[name] = component
            return True
        return False

    def get_one(self, name: str) -> Optional[T]:
        """
        Retrieve a single element by name.

        Args:
            name: Name of the element.

        Returns:
            The element if found, otherwise None.
        """
        return self._components.get(name)

    def get_all(self) -> Dict[str, T]:
        """
        Retrieve all elements in the set.

        Returns:
            A dictionary mapping element names to elements.
        """
        return self._components

    def update(self, old_name: str, new_name: str) -> bool:
        """
        Rename an element within the set.

        Args:
            old_name: Current element name.
            new_name: New element name.

        Returns:
            True if the element was renamed successfully, False if the
            old name does not exist or the new name is already in use.
        """
        if self._exists(old_name) and self._not_exists(new_name):
            component = self._components.pop(old_name)
            self._components[new_name] = component
            return True
        return False

    def delete_one(self, name: str) -> bool:
        """
        Remove an element from the set.

        Args:
            name: Name of the element to delete.

        Returns:
            True if the element was removed, False if it did not exist.
        """
        return self._components.pop(name, None) is not None

    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of the set contents.

        The summary adapts automatically depending on whether the stored
        elements are declarative classes or runtime instances.
        """
        result: Dict[str, Any] = {}

        for name, component in self.get_all().items():
            if isinstance(component, type) and issubclass(component, FraguaClass):
                cls = cast(Type[FraguaClass], component)
                result[name] = cls.summary()

            elif isinstance(component, FraguaInstance):
                result[name] = component.summary()

            else:
                raise TypeError(
                    f"Unsupported component type in FraguaSet '{self.set_name}': "
                    f"{type(component).__name__}"
                )

        return result
