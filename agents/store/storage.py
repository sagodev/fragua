"""
Efficient in-memory storage for Fragua ETL objects.
"""

from datetime import datetime
from utils.metrics import calculate_checksum


class Storage:
    """
    Stores objects in a centralized dict by type with minimal metadata.
    Prepares for lazy loading and checksum verification.
    """

    def __init__(self):
        # type -> name -> {obj, saved_at, checksum, data_ref}
        self._store = {
            "wagon": {},
            "box": {},
            "container": {},
        }

    def add(self, obj_type: str, name: str, obj: object, compute_checksum: bool = True):
        """Add an object with metadata to storage."""
        checksum = None
        if compute_checksum:
            # calculate checksum if object has 'data', otherwise use the object itself
            if hasattr(obj, "data"):
                checksum = calculate_checksum(obj.data)
            else:
                checksum = calculate_checksum(obj)
        self._store[obj_type][name] = {
            "obj": obj,
            "saved_at": datetime.utcnow(),
            "checksum": checksum,
            "data_ref": None,  # placeholder for lazy loading
        }

    def get(self, obj_type: str, name: str):
        """Retrieve an object from storage."""
        entry = self._store[obj_type].get(name)
        if entry:
            return entry["obj"]
        return None

    def remove(self, obj_type: str, name: str):
        """Remove an object from storage."""
        return self._store[obj_type].pop(name, None)

    def exists(self, obj_type: str, name: str) -> bool:
        return name in self._store[obj_type]

    def list_all(self, obj_type: str):
        return list(self._store[obj_type].keys())
