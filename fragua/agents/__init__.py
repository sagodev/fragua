"""Fragua Agents package."""

# ------------------- Agents ------------------- #
from .transformer import Transformer
from .loader import Loader
from .warehouse_manager import WarehouseManager


# ------------------- __all__ ------------------- #
__all__ = [
    # Roles
    "WarehouseManager",
    "Transformer",
    "Loader",
]
