"""
Containers for storing loaded data before final delivery.

Containers allow versioned storage of data that has been processed and is ready for delivery.
"""

from fragua.core.storage import Storage, T


class Container(Storage[T]):
    """Container for processed data ready for delivery."""
