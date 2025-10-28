"""
Storage types for storing different types of data.
"""

from fragua.core.storage import register_storage, T
from fragua.store.store import Storage


@register_storage
class Wagon(Storage[T]):
    """Storage type for storing raw data."""


@register_storage
class Box(Storage[T]):
    """Storage type for storing forged data."""


@register_storage
class Container(Storage[T]):
    """Storage type for storing delivery data."""
