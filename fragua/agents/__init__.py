"""Fragua Agents package."""

# ------------------- Agents ------------------- #
from .extractor import Extractor
from .transformer import Transformer
from .loader import Loader
from .warehouse_manager import WarehouseManager


# ------------------- __all__ ------------------- #
__all__ = [
    # Roles
    "WarehouseManager",
    "Extractor",
    "Transformer",
    "Loader",
]
