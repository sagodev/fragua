"""
Boxes for storing transformed data from Blacksmiths.

Boxes provide versioned storage for transformed data before loading.
"""

from fragua.core.storage import Storage, T


class Box(Storage[T]):
    """Container for temporary storage of raw or intermediate data."""
