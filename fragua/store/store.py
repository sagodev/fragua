"""
Lightweight in-memory store structure.
The StoreManager handles all the logic.
"""

from typing import Dict, Union
from fragua.store.storage_types import Wagon, Box


class Store:
    """
    Simple container for Wagons and Boxes.
    StoreManager is responsible for all operations.
    """

    VALID_TYPES = (Wagon, Box)

    def __init__(self, store_name: str = "store") -> None:
        """
        Initialize a Store.

        Args:
            store_name (str): Name of the store.
        """
        self.store_name = store_name
        self._store: Dict[str, Union[Wagon, Box]] = {}

    @property
    def data(self) -> Dict[str, Union[Wagon, Box]]:
        """
        Expose the raw internal storage mapping.

        Returns: Dict[str, Union[Wagon, Box]]: Stored objects by name.
        """
        return self._store
