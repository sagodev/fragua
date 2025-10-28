"""Fragua Core module"""

# ------------------- Store ------------------- #
from .store import Store

# ------------------- Storage ------------------- #
from .storage import Storage, register_storage, get_storage, list_storages


# ------------------- __all__ ------------------- #
__all__ = [
    # Store
    "Store",
    # Storage
    "Storage",
    "register_storage",
    "get_storage",
    "list_storages",
]
