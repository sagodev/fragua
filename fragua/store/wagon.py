"""
Wagons for storing extracted data from Miners.

Wagons provide temporary storage and versioning for raw data.
"""

from fragua.core.base_storage import BaseStorage, T


class Wagon(BaseStorage[T]):
    """Special container for delivering data between agents."""
