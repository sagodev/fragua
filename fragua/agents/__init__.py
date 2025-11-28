"""Fragua Agents package."""

# ------------------- Agents ------------------- #
from .loader import Loader
from .warehouse_manager import WarehouseManager


# ------------------- __all__ ------------------- #
__all__ = [
    # Roles
    "WarehouseManager",
    "Loader",
]
