"""Fragua Store package."""

# ------------------- Storage class ------------------- #
from .storage import Storage


# ------------------- Storage types ------------------- #
from .storage_types import (
    Box,
    Container,
    STORAGE_CLASSES,
)


# ------------------- __all__ ------------------- #
__all__ = [
    # Storage class
    "Storage",
    # Storage types
    "STORAGE_CLASSES",
    "Box",
    "Container",
]
