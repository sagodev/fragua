"""
Efficient in-memory storage for Fragua ETL objects.
"""


from datetime import datetime, UTC
from typing import Any, Dict, Optional
from utils.metrics import calculate_checksum


class Storage:
    """
    Stores objects in a centralized dict by type with minimal metadata.
    Prepares for lazy loading and checksum verification.
    """

    # Define the type for the metadata dictionary
    _Entry = Dict[str, Any]
    _StoreType = Dict[str, Dict[str, _Entry]]

    def __init__(self) -> None:
        # type -> name -> {obj, saved_at, checksum, data_ref}
        self._store: Storage._StoreType = {
            "wagon": {},
            "box": {},
            "container": {},
        }

    def add(self, obj_type: str, name: str, obj: object, compute_checksum: bool = True) -> None:
        """Add an object with metadata to storage."""
        checksum: Optional[str] = None
        if compute_checksum:
            # calculate checksum if object has 'data', otherwise use the object itself
            if hasattr(obj, "data"):
                checksum = calculate_checksum(getattr(obj, "data"))
            else:
                checksum = calculate_checksum(obj)
        self._store[obj_type][name] = {
            "obj": obj,
            "saved_at": datetime.now(UTC),
            "checksum": checksum,
            "data_ref": None,  # placeholder for lazy loading
        }

    def get(self, obj_type: str, name: str) -> Optional[object]:
        """Retrieve an object from storage."""
        entry: Optional[Storage._Entry] = self._store[obj_type].get(name)
        if entry:
            return entry["obj"]
        return None

    def remove(self, obj_type: str, name: str) -> Optional[object]:
        """Remove an object from storage."""
        entry: Optional[Storage._Entry] = self._store[obj_type].pop(name, None)
        if entry:
            return entry.get("obj")
        return None

    def get_checksum(self, obj_type: str, name: str) -> Optional[str]:
        """Return the stored checksum for an object, or None if not found."""
        entry: Optional[Storage._Entry] = self._store.get(obj_type, {}).get(name)
        if not entry:
            return None
        return entry.get("checksum")

    def exists(self, obj_type: str, name: str) -> bool:
        return name in self._store[obj_type]

    def list_all(self, obj_type: str) -> list[str]:
        return list(self._store[obj_type].keys())
