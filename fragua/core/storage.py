"""
Base storage class for all storage objects in Fragua (Wagon, Box, Container).
"""

from typing import Any, Dict, Generic, Optional, TypeVar
from fragua.utils.logger import get_logger
from fragua.utils.metrics import add_metadata_to_storage, generate_metadata

T = TypeVar("T")

logger = get_logger(__name__)


class Storage(Generic[T]):
    """Core storage unit containing data and unified metadata handling."""

    def __init__(self, data: Optional[T] = None) -> None:
        self._data: Optional[T] = data
        self._metadata: dict[str, object] = {}

        if data is not None:
            self._generate_base_metadata()

    @property
    def data(self) -> T:
        """
        Return the stored data.
        Raises:
            ValueError: if accessed before being initialized.
        """
        if self._data is None:
            raise ValueError(f"{self.__class__.__name__} has no data assigned yet.")
        return self._data

    @data.setter
    def data(self, value: T) -> None:
        """Set or replace the stored data."""
        self._data = value
        self._generate_base_metadata()

    @property
    def metadata(self) -> dict[str, object]:
        """Return the current metadata of the storage."""
        return self._metadata

    @metadata.setter
    def metadata(self, value: dict[str, object]) -> None:
        self._metadata = value

    def _generate_base_metadata(self) -> None:
        """Generate and attach base metadata."""
        metadata = generate_metadata(self, metadata_type="base")
        add_metadata_to_storage(self, metadata)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class Box(Storage[Any]):
    """Storage type for transformed data."""


class Container(Storage[Any]):
    """
    Storage designed to contain  Boxes.
    """

    def __init__(self) -> None:
        super().__init__(data=None)
        self._content: Dict[str, Box] = {}

    def add_storage(self, storage_name: str, storage: Box) -> None:
        """Add a sub-storage Box to the container."""
        self._content[storage_name] = storage

    def get_storage(self, name: str) -> Box:
        """Retrieve a specific sub-storage by name."""
        return self._content[name]

    def list_storages(self) -> dict[str, str]:
        """Return a mapping of contained storages: name -> type."""
        return {name: s.__class__.__name__ for name, s in self._content.items()}

    def remove_storage(self, name: str) -> None:
        """Remove a sub-storage by name."""
        self._content.pop(name, None)

    def clear(self) -> None:
        """Remove all contained storages."""
        self._content.clear()

    def __repr__(self) -> str:
        items = ", ".join(self._content.keys()) or "empty"
        return f"<Container: {items}>"


STORAGE_CLASSES: dict[str, type[Storage[Any]]] = {
    "Box": Box,
    "Container": Container,
}
