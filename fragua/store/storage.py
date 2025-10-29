"""
Base storage class for all storage objects in Fragua (Wagon, Box, Container).
"""

from typing import Generic, Optional, TypeVar, Type, Any, Dict
from fragua.utils.logger import get_logger
from fragua.utils.metrics import add_metadata_to_storage, generate_metadata

T = TypeVar("T")
S = TypeVar("S", bound="Storage[Any]")

logger = get_logger(__name__)


class Storage(Generic[T]):
    """Core storage unit containing data and unified metadata handling."""

    def __init__(self, data: Optional[T] = None):
        self.data: Optional[T] = data
        self._metadata: dict[str, object] = {}

        if data is not None:
            self._generate_base_metadata()

    def _generate_base_metadata(self) -> None:
        """Generate and attach base metadata."""
        metadata = generate_metadata(self, metadata_type="base")
        add_metadata_to_storage(self, metadata)

    @property
    def metadata(self) -> dict[str, object]:
        """Return the current metadata of the storage."""
        return self._metadata

    @metadata.setter
    def metadata(self, value: dict[str, object]) -> None:
        self._metadata = value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


# -------------------- GLOBAL STORAGE REGISTRY -------------------- #
STORAGE_REGISTRY: Dict[str, Type[Storage[Any]]] = {}


def register_storage(cls: Type[S]) -> Type[S]:
    """Register a Storage subclass in the global registry."""
    STORAGE_REGISTRY[cls.__name__] = cls
    return cls


def get_storage(name: str) -> Type[Storage[Any]]:
    """Retrieve a Storage subclass from the registry by name."""
    if name not in STORAGE_REGISTRY:
        raise KeyError(f"Storage class '{name}' not registered.")
    return STORAGE_REGISTRY[name]


def list_storages() -> list[str]:
    """Return a list of all registered storage class names."""
    return list(STORAGE_REGISTRY.keys())
