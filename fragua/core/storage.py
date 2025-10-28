"""
Base storage class for all storage objects in Fragua (Wagon, Box, Container).
"""

from typing import Generic, Optional, TypeVar, Type, Any
from fragua.utils.logger import get_logger
from fragua.utils.metrics import (
    add_metadata_to_storage,
    generate_metadata,
)

T = TypeVar("T")

logger = get_logger(__name__)


class Storage(Generic[T]):
    """Core storage unit containing data and unified metadata handling."""

    def __init__(self, data: Optional[T] = None):
        """
        Initialize a Storage instance.

        Args:
            name: Name of the storage object.
            data: Optional data payload.
        """
        self.data: Optional[T] = data
        self._metadata: dict[str, object] = {}

        if data is not None:
            self._generate_base_metadata()

    def _generate_base_metadata(self) -> None:
        """Generate and attach base metadata."""
        metadata = generate_metadata(self, metadata_type="base")
        add_metadata_to_storage(self, metadata)

    # -------------------- METADATA HANDLING -------------------- #
    @property
    def metadata(self) -> dict[str, object]:
        """Return the current metadata of the storage."""
        return self._metadata

    @metadata.setter
    def metadata(self, value: dict[str, object]) -> None:
        self._metadata = value

    # -------------------- REPRESENTATION -------------------- #
    def __repr__(self) -> str:
        """String representation showing the name and type."""
        return f"<{self.__class__.__name__}>"


STORAGE_REGISTRY: dict[str, Type[Storage[Any]]] = {}


def register_storage(cls: Type[Storage[Any]]) -> Type[Storage[Any]]:
    """
    Register a Storage subclass in the global registry.

    Args:
        cls: A subclass of Storage to register.

    Returns:
        The same class (allows decorator usage).
    """
    STORAGE_REGISTRY[cls.__name__] = cls
    return cls


def get_storage(name: str) -> Type[Storage[Any]]:
    """
    Retrieve a Storage subclass from the registry by name.

    Args:
        name: Name of the registered storage class.

    Returns:
        Storage subclass.

    Raises:
        KeyError if class not found.
    """
    if name not in STORAGE_REGISTRY:
        raise KeyError(f"Storage class '{name}' not registered.")
    return STORAGE_REGISTRY[name]


def list_storages() -> list[str]:
    """
    Return a list of all registered storage class names.
    """
    return list(STORAGE_REGISTRY.keys())
