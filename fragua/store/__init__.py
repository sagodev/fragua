"""Fragua Store package."""

# ------------------- Storage Class ------------------- #
from .storage import Storage

# ------------------- Store Class ------------------- #
from .store import Store

# ------------------- Storage Types ------------------- #
from .storage_types import (
    Box,
    Wagon,
    Container,
    STORAGE_REGISTRY,
    register_storage,
    get_storage,
    list_storages,
)


# ------------------- __all__ ------------------- #
__all__ = [
    "Store",
    "Storage",
    # Storage Types
    "Wagon",
    "Box",
    "Container",
    # Storage Registry Functions
    "STORAGE_REGISTRY",
    "register_storage",
    "get_storage",
    "list_storages",
]
