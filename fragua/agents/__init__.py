"""Fragua Agents package."""

# ------------------- Agents ------------------- #
from .agent import Agent
from .extractor import Extractor
from .transformer import Transformer
from .loader import Loader
from .warehouse_manager import WarehouseManager


# ------------------- __all__ ------------------- #
__all__ = [
    # Agent Class
    "Agent",
    # Roles
    "WarehouseManager",
    "Extractor",
    "Transformer",
    "Loader",
]
