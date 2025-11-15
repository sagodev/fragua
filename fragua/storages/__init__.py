"""Fragua Store package."""

# ------------------- Storage class ------------------- #
from .storage import Storage

# ------------------- Warehouse class ------------------- #
from .warehouse import Warehouse

# ------------------- Storage types ------------------- #
from .storage_types import (
    Box,
    Container,
    STORAGE_CLASSES,
)


# ------------------- __all__ ------------------- #
__all__ = [
    # Warehouse class
    "Warehouse",
    # Storage class
    "Storage",
    # Storage types
    "STORAGE_CLASSES",
    "Box",
    "Container",
]
