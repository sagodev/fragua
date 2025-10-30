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
    "register_storage",
    "get_storage",
    "list_storages",
]
