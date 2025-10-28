"""
Wagons for storing extracted data from Miners.

Wagons provide temporary storage and versioning for raw data.
"""

from fragua.core.storage import Storage, T


class Wagon(Storage[T]):
    """Special container for delivering data between agents."""
