"""
Base storage class for all storage objects in Fragua (Wagon, Box, Container).
"""

from typing import Any, Dict, Generic, Optional, TypeVar
from fragua.utils.logger import get_logger
from fragua.utils.metrics import add_metadata_to_storage, generate_metadata

T = TypeVar("T")

logger = get_logger(__name__)


class Storage(Generic[T]):
    """
    Core storage abstraction for all persistable objects in Fragua.

    A Storage instance encapsulates data along with a unified metadata
    model. Metadata is automatically generated and attached whenever
    data is assigned, enabling traceability, observability, and lineage
    tracking across the ETL workflow.

    Concrete storage types (e.g., Box, Container) specialize how data
    is organized, but share the same metadata lifecycle.
    """

    def __init__(self, data: Optional[T] = None) -> None:
        """
        Initialize the storage with optional data.

        Args:
            data: Optional initial data to store. If provided, base
                metadata is generated automatically.
        """
        self._data: Optional[T] = data
        self._metadata: dict[str, object] = {}

        if data is not None:
            self._generate_base_metadata()

    @property
    def data(self) -> T:
        """
        Return the stored data.

        Raises:
            ValueError: If the storage has not been initialized with data.
        """
        if self._data is None:
            raise ValueError(f"{self.__class__.__name__} has no data assigned yet.")
        return self._data

    @data.setter
    def data(self, value: T) -> None:
        """
        Set or replace the stored data.

        Assigning data regenerates the base metadata to reflect the
        updated state.

        Args:
            value: Data to store.
        """
        self._data = value
        self._generate_base_metadata()

    @property
    def metadata(self) -> dict[str, object]:
        """
        Return the metadata associated with this storage.

        Returns:
            A dictionary containing metadata entries.
        """
        return self._metadata

    @metadata.setter
    def metadata(self, value: dict[str, object]) -> None:
        """
        Replace the entire metadata mapping.

        Args:
            value: New metadata dictionary.
        """
        self._metadata = value

    def _generate_base_metadata(self) -> None:
        """
        Generate and attach base metadata to the storage.

        Base metadata typically includes information such as storage type,
        creation context, and timestamps.
        """
        metadata = generate_metadata(self, metadata_type="base")
        add_metadata_to_storage(self, metadata)

    def __repr__(self) -> str:
        """
        Return a concise string representation of the storage.

        Returns:
            A string identifying the storage class.
        """
        return f"<{self.__class__.__name__}>"


class Box(Storage[Any]):
    """
    Storage type representing a single unit of data.

    A Box typically contains the output of a style execution and is the
    most common persistable storage unit within the warehouse.
    """


class Container(Storage[Any]):
    """
    Composite storage capable of grouping multiple Box instances.

    A Container acts as a hierarchical storage structure, allowing
    multiple Boxes to be stored and managed under a single logical unit.
    """

    def __init__(self) -> None:
        """
        Initialize an empty Container.

        Containers do not hold direct data; instead, they manage a
        collection of named Box instances.
        """
        super().__init__(data=None)
        self._content: Dict[str, Box] = {}

    def add_storage(self, storage_name: str, storage: Box) -> None:
        """
        Add a Box to the container.

        Args:
            storage_name: Name under which the Box will be stored.
            storage: Box instance to add.
        """
        self._content[storage_name] = storage

    def get_storage(self, name: str) -> Box:
        """
        Retrieve a Box from the container by name.

        Args:
            name: Name of the Box.

        Returns:
            The requested Box instance.
        """
        return self._content[name]

    def list_storages(self) -> dict[str, str]:
        """
        List all contained storages.

        Returns:
            A mapping of storage names to their class names.
        """
        return {name: s.__class__.__name__ for name, s in self._content.items()}

    def remove_storage(self, name: str) -> None:
        """
        Remove a Box from the container.

        Args:
            name: Name of the Box to remove.
        """
        self._content.pop(name, None)

    def clear(self) -> None:
        """
        Remove all contained Boxes from the container.
        """
        self._content.clear()

    def __repr__(self) -> str:
        """
        Return a string representation of the container and its contents.

        Returns:
            A string listing contained storage names or indicating emptiness.
        """
        items = ", ".join(self._content.keys()) or "empty"
        return f"<Container: {items}>"


STORAGE_CLASSES: dict[str, type[Storage[Any]]] = {
    "Box": Box,
    "Container": Container,
}
