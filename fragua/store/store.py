"""
Flexible in-memory store for Fragua ETL objects.
"""

from datetime import datetime, timezone
from typing import Dict, Optional, Literal, Union, List
from fragua.utils.metrics import calculate_checksum


class Store:
    """
    Generic store that holds ETL objects (wagon, box, container) with metadata.
    It can be configured to handle one, several, or all object types.
    """

    _Entry = Dict[str, object]
    _StoreType = Dict[str, Dict[str, _Entry]]

    VALID_TYPES = ("wagon", "box", "container")

    def __init__(
        self,
        store_name: str,
        store_types: Union[
            Literal["wagon", "box", "container", "all"], List[str]
        ] = "all",
    ) -> None:
        """
        Initialize the store with a given name and the object types it can manage.

        Args:
            store_name: Identifier name for the store instance.
            store_types: One or multiple object types to handle.
                        Use 'all' to include all supported types.
        """
        self.store_name = store_name

        # Normalize the types to a list
        if store_types == "all":
            types_to_store = list(self.VALID_TYPES)
        elif isinstance(store_types, str):
            types_to_store = [store_types]
        else:
            # Ensure only valid types are included
            types_to_store = [t for t in store_types if t in self.VALID_TYPES]

        # Build the internal store dynamically
        self._store: Store._StoreType = {t: {} for t in types_to_store}

    def add(
        self,
        obj_type: Literal["wagon", "box", "container"],
        name: str,
        obj: object,
        compute_checksum: bool = True,
    ) -> None:
        """Add an object with metadata to the store."""
        if obj_type not in self._store:
            raise ValueError(f"Object type '{obj_type}' not allowed in this store.")

        checksum: Optional[str] = None
        if compute_checksum:
            if hasattr(obj, "data"):
                checksum = calculate_checksum(getattr(obj, "data"))
            else:
                checksum = calculate_checksum(obj)

        self._store[obj_type][name] = {
            "obj": obj,
            "saved_at": datetime.now(timezone.utc),
            "checksum": checksum,
            "data_ref": None,
        }

    def get(self, obj_type: str, name: str) -> Optional[object]:
        """Retrieve an object from the store."""
        entry: Optional[Store._Entry] = self._store.get(obj_type, {}).get(name)
        return entry["obj"] if entry else None

    def remove(self, obj_type: str, name: str) -> Optional[object]:
        """Remove an object from the store."""
        entry: Optional[Store._Entry] = self._store.get(obj_type, {}).pop(name, None)
        return entry["obj"] if entry else None

    def get_checksum(self, obj_type: str, name: str) -> Optional[str]:
        """Return the stored checksum for an object, or None if not found."""
        entry: Optional[Store._Entry] = self._store.get(obj_type, {}).get(name)
        checksum = entry.get("checksum") if entry else None
        return checksum if isinstance(checksum, str) else None

    def exists(self, obj_type: str, name: str) -> bool:
        """Check if an object exists in the store."""
        return name in self._store.get(obj_type, {})

    def list_all(self, obj_type: Optional[str] = None) -> List[str]:
        """
        List all object names of a given type or all types in the store.

        Args:
            obj_type: Optional type to list. If None, list all stored objects.
        """
        if obj_type:
            return list(self._store.get(obj_type, {}).keys())
        # List all objects across all stored types
        all_names: list[str] = []
        for t, entries in self._store.items():
            all_names.extend(entries.keys())
        return all_names
