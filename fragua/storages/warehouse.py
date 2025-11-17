"""
Lightweight in-memory store structure.
The StoreManager handles all the logic.
"""

from typing import Dict
from fragua.storages.storage import Storage
from fragua.storages.storage_types import Box


class Warehouse:
    """
    Simple container for Boxes.
    Warehouse manager is responsible for all operations.
    """

    def __init__(self, warehouse_name: str = "warehouse") -> None:
        """
        Initialize a warehouse.

        Args:
            warehouse_name (str): Name of the warehouse.
        """
        self.warehouse_name = warehouse_name
        self._warehouse: Dict[str, Storage[Box]] = {}

    @property
    def data(self) -> Dict[str, Storage[Box]]:
        """
        Expose the raw internal storage mapping.

        Returns: Dict[str, Storage[Box]]: Stored objects by name.
        """
        return self._warehouse

    def summary(self) -> Dict[str, object]:
        """
        Return a JSON-serializable summary of the Warehouse contents.

        Includes:
            - warehouse name
            - number of storage items
            - mapping of storage names -> class name
        """
        storages_info: Dict[str, str] = {
            name: obj.__class__.__name__ for name, obj in self._warehouse.items()
        }

        return {
            "warehouse_name": self.warehouse_name,
            "storage_count": len(self._warehouse),
            "storages": storages_info,
        }
