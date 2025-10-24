"""
StoreManager agent for Fragua ETL.
Manages Wagons, Boxes, and Containers using in-memory Store.
Handles metadata, checksums, lazy logging, and reporting with minimal code.
"""

from datetime import datetime, timezone
from typing import Dict, Optional, Literal
import pandas as pd
from fragua.store.store import Store
from fragua.utils.metrics import calculate_checksum
from fragua.utils.logger import get_logger

ObjType = Literal["wagon", "box", "container"]


class StoreManager:
    """Dynamic StoreManager that works only with types defined in the Store."""

    def __init__(self, store: Store, name: str = "StoreManager") -> None:
        self.name = name
        self.logger = get_logger(name)
        self.store = store  # External Store instance
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
        """Record metadata about a store operation."""
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

        stored_checksum = self.store.get_checksum(obj_type, obj_name)
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
    def _validate_type(self, obj_type: str) -> None:
        """Ensure the object type is allowed by the Store."""
        if obj_type not in self.store._store:
            raise ValueError(f"Object type '{obj_type}' is not managed by this Store.")

    def save(
        self, obj_type: str, name: str, obj: object, overwrite: bool = False
    ) -> None:
        """Save an object into the store."""
        self._validate_type(obj_type)

        if self.store.exists(obj_type, name) and not overwrite:
            self.logger.warning(
                "[%s] %s '%s' exists. Use overwrite=True to replace.",
                self.name,
                obj_type,
                name,
            )
            return

        self.logger.info("[%s] Saving %s: %s", self.name, obj_type, name)
        self.store.add(obj_type, name, obj)
        self._record_metadata(name, obj_type, "save", obj)

    def load(self, obj_type: str, name: str) -> Optional[object]:
        """Load an object from the store."""
        self._validate_type(obj_type)
        obj = self.store.get(obj_type, name)
        self._verify_on_load(obj_type, name, obj)
        return obj

    def remove(self, obj_type: str, name: str) -> Optional[object]:
        """Remove an object from the store."""
        self._validate_type(obj_type)
        obj = self.store.remove(obj_type, name)
        if obj:
            self._record_metadata(name, obj_type, "remove", obj)
        else:
            self.logger.warning(
                "[%s] %s '%s' does not exist.", self.name, obj_type, name
            )
        return obj

    def has(self, obj_type: str, name: str) -> bool:
        """Check if an object exists in the store."""
        self._validate_type(obj_type)
        return self.store.exists(obj_type, name)

    # ------------------- Reporting ------------------- #
    def report(self) -> pd.DataFrame:
        """Return a copy of the metadata report."""
        return self.metadata.copy()

    def list_all(self) -> Dict[str, list[str]]:
        """List all stored objects by type."""
        return {
            obj_type: self.store.list_all(obj_type) for obj_type in self.store._store
        }

    def __repr__(self) -> str:
        """String representation of the StoreManager."""
        return f"<StoreManager name={self.name}>"
