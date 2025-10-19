"""
StorageManager agent for Fragua ETL.
Manages Wagons, Boxes, and Containers using pure in-memory Storage.
Handles metadata, checksums, lazy logging, and reporting with minimal code.
"""

from datetime import datetime, timezone
from typing import Dict, Optional
import pandas as pd
from fragua.agents.store.storage import Storage
from fragua.utils.metrics import calculate_checksum
from fragua.utils.logger import get_logger


class StorageManager:
    """Ultra-dynamic StorageManager using optimized Storage."""

    TYPE_MAP: Dict[str, str] = {
        "wagon": "wagon",
        "box": "box",
        "container": "container",
    }

    def __init__(self, name: str = "StorageManager") -> None:
        self.name = name
        self.logger = get_logger(name)
        self.storage = Storage()
        # Metadata log for all operations
        self.metadata = pd.DataFrame(
            columns=[
                "object_name",
                "object_type",
                "timestamp",
                "rows",
                "columns",
                "checksum",
                "operation",
            ]
        )

    # ------------------- Internal helpers ------------------- #
    def _record_metadata(
        self, obj_name: str, obj_type: str, operation: str, obj: object
    ) -> None:
        """Record metadata about a storage operation."""
        rows: Optional[int] = None
        cols: Optional[int] = None
        checksum: Optional[str] = None

        if hasattr(obj, "data") and hasattr(obj.data, "shape"):
            rows, cols = obj.data.shape
            checksum = calculate_checksum(obj.data)
        else:
            checksum = calculate_checksum(obj)

        new_row = {
            "object_name": obj_name,
            "object_type": obj_type,
            "timestamp": datetime.now(timezone.utc),
            "rows": rows,
            "columns": cols,
            "checksum": checksum,
            "operation": operation,
        }
        self.metadata = pd.concat(
            [self.metadata, pd.DataFrame([new_row])], ignore_index=True
        )

    def _verify_on_load(
        self, obj_type: str, obj_name: str, obj: Optional[object]
    ) -> None:
        """Verify checksum integrity when loading an object."""
        if obj is None:
            return

        stored_checksum = self.storage.get_checksum(obj_type, obj_name)
        if stored_checksum is None:
            self.logger.warning(
                "[%s] No checksum recorded for '%s' (%s)", self.name, obj_name, obj_type
            )
            return

        current_checksum = calculate_checksum(obj.data if hasattr(obj, "data") else obj)
        if stored_checksum != current_checksum:
            self.logger.error(
                "[%s] Checksum mismatch for '%s' (%s)", self.name, obj_name, obj_type
            )
        else:
            self.logger.info(
                "[%s] Checksum verified for '%s' (%s)", self.name, obj_name, obj_type
            )

    # ------------------- Public generic methods ------------------- #
    def save(
        self, obj_type: str, name: str, obj: object, overwrite: bool = False
    ) -> None:
        """Save an object into storage."""
        if obj_type not in self.TYPE_MAP:
            raise ValueError(f"Unknown object type '{obj_type}'")

        coll_name = self.TYPE_MAP[obj_type]
        if self.storage.exists(coll_name, name) and not overwrite:
            self.logger.warning(
                "[%s] %s '%s' exists. Use overwrite=True to replace.",
                self.name,
                obj_type,
                name,
            )
            return

        self.logger.info("[%s] Saving %s: %s", self.name, obj_type, name)
        self.storage.add(coll_name, name, obj)
        self._record_metadata(name, obj_type, "save", obj)

    def load(self, obj_type: str, name: str) -> Optional[object]:
        """Load an object from storage."""
        coll_name = self.TYPE_MAP[obj_type]
        obj = self.storage.get(coll_name, name)
        self._verify_on_load(coll_name, name, obj)
        return obj

    def remove(self, obj_type: str, name: str) -> Optional[object]:
        """Remove an object from storage."""
        coll_name = self.TYPE_MAP[obj_type]
        obj = self.storage.remove(coll_name, name)
        if obj:
            self._record_metadata(name, obj_type, "remove", obj)
        else:
            self.logger.warning(
                "[%s] %s '%s' does not exist.", self.name, obj_type, name
            )
        return obj

    def has(self, obj_type: str, name: str) -> bool:
        """Check if an object exists in storage."""
        coll_name = self.TYPE_MAP[obj_type]
        return self.storage.exists(coll_name, name)

    # ------------------- Reporting ------------------- #
    def report(self) -> pd.DataFrame:
        """Return a copy of the metadata report."""
        return self.metadata.copy()

    def list_all(self) -> Dict[str, list[str]]:
        """List all stored objects by type."""
        return {
            obj_type: self.storage.list_all(coll_name)
            for obj_type, coll_name in self.TYPE_MAP.items()
        }

    def __repr__(self) -> str:
        """String representation of the StorageManager."""
        return f"<StorageManager name={self.name}>"
