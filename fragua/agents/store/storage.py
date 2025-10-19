"""
Efficient in-memory storage for Fragua ETL objects.
"""

from datetime import datetime, timezone
from typing import Dict, Optional, Literal
from fragua.utils.metrics import calculate_checksum


class Storage:
    """
    Stores objects in a centralized dict by type with minimal metadata.
    Prepares for lazy loading and checksum verification.
    """

    _Entry = Dict[str, object]
    _StoreType = Dict[str, Dict[str, _Entry]]

    def __init__(self) -> None:
        self._store: Storage._StoreType = {
            "wagon": {},
            "box": {},
            "container": {},
        }

    def add(
        self,
        obj_type: Literal["wagon", "box", "container"],
        name: str,
        obj: object,
        compute_checksum: bool = True,
    ) -> None:
        """Add an object with metadata to storage."""
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

    def get(
        self, obj_type: Literal["wagon", "box", "container"], name: str
    ) -> Optional[object]:
        """Retrieve an object from storage."""
        entry: Optional[Storage._Entry] = self._store[obj_type].get(name)
        if entry:
            return entry["obj"]
        return None

    def remove(
        self, obj_type: Literal["wagon", "box", "container"], name: str
    ) -> Optional[object]:
        """Remove an object from storage."""
        entry: Optional[Storage._Entry] = self._store[obj_type].pop(name, None)
        if entry:
            return entry["obj"]
        return None

    def get_checksum(
        self, obj_type: Literal["wagon", "box", "container"], name: str
    ) -> Optional[str]:
        """Return the stored checksum for an object, or None if not found."""
        entry: Optional[Storage._Entry] = self._store.get(obj_type, {}).get(name)
        if not entry:
            return None
        checksum = entry.get("checksum")
        return checksum if isinstance(checksum, str) else None

    def exists(self, obj_type: Literal["wagon", "box", "container"], name: str) -> bool:
        """Check if an object exists in storage."""
        return name in self._store[obj_type]

    def list_all(self, obj_type: Literal["wagon", "box", "container"]) -> list[str]:
        """List all object names of a given type in storage."""
        return list(self._store[obj_type].keys())
