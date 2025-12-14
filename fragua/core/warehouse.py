"""
Lightweight in-memory store structure.
"""

from typing import Dict
from fragua.core.component import FraguaComponent
from fragua.core.storage import Storage, Box


class FraguaWarehouse(FraguaComponent):
    """
    Lightweight in-memory container for persisted storage objects.

    FraguaWarehouse acts as a passive data holder for Storage instances
    (typically Boxes). All mutation and access logic is delegated to the
    WarehouseManager, making this class responsible only for state
    representation and introspection.
    """

    def __init__(self, warehouse_name: str = "warehouse") -> None:
        """
        Initialize the warehouse container.

        Args:
            warehouse_name: Identifier used to reference this warehouse
                within the environment.
        """
        super().__init__(component_name=warehouse_name)
        self._warehouse: Dict[str, Storage[Box]] = {}

    @property
    def data(self) -> Dict[str, Storage[Box]]:
        """
        Expose the internal storage mapping.

        This property provides read access to the raw mapping of storage
        names to Storage instances. Mutation should be performed
        exclusively through the WarehouseManager.

        Returns:
            A dictionary mapping storage names to Storage[Box] instances.
        """
        return self._warehouse

    def summary(self) -> Dict[str, object]:
        """
        Generate a structured summary of the warehouse contents.

        The summary is JSON-serializable and intended for diagnostics,
        observability, and debugging.

        Returns:
            A dictionary containing:
                - warehouse_name: Name of the warehouse
                - storage_count: Number of stored items
                - storages: Mapping of storage names to storage class names
        """
        storages_info: Dict[str, str] = {
            name: obj.__class__.__name__ for name, obj in self._warehouse.items()
        }

        return {
            "warehouse_name": self.name,
            "storage_count": len(self._warehouse),
            "storages": storages_info,
        }
