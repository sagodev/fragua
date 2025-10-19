"""
Boxes for storing transformed data from Blacksmiths.

Boxes provide versioned storage for transformed data before loading.
"""

from fragua.core.base_storage import BaseStorage, T


class Box(BaseStorage[T]):
    """Container for temporary storage of raw or intermediate data."""
