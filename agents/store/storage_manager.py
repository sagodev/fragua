"""
StorageManager agent for Fragua ETL.
Provides centralized storage interface with full metadata tracking,
checksums, lazy logging, and automatic data integrity verification on load.
"""

import pandas as pd
from datetime import datetime, UTC
from agents.store.storage import Storage
from utils.logger import get_logger
from utils.metrics import calculate_checksum


class StorageManager:
    """
    Central manager that interacts with Storage, tracks metadata,
    checksums, and automatically verifies integrity on load.
    """

    def __init__(self, name: str = "StorageManager"):
        self.name = name
        self.logger = get_logger(name)
        self.storage = Storage()

        # DataFrame to track all storage operations
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

    # ------------------- Internal helper ------------------- #
    def _record_metadata(
        self, obj_name: str, obj_type: str, operation: str, obj: object
    ):
        """Record metadata and checksum for a storage operation."""
        rows, cols, checksum = None, None, None
        if hasattr(obj, "data") and hasattr(obj.data, "shape"):
            rows, cols = obj.data.shape
            checksum = calculate_checksum(obj.data)
        else:
            checksum = calculate_checksum(obj)

        new_row = {
            "object_name": obj_name,
            "object_type": obj_type,
            "timestamp": datetime.now(UTC),
            "rows": rows,
            "columns": cols,
            "checksum": checksum,
            "operation": operation,
        }
        self.metadata = pd.concat(
            [self.metadata, pd.DataFrame([new_row])], ignore_index=True
        )

    def _verify_on_load(self, obj_name: str, obj_type: str, obj: object):
        """Verify checksum and log on object load."""
        if obj is None:
            return
        meta_rows = self.metadata[
            (self.metadata["object_name"] == obj_name)
            & (self.metadata["object_type"] == obj_type)
            & (self.metadata["operation"] == "save")
        ]
        if meta_rows.empty:
            self.logger.warning(
                "[%s] No checksum recorded for '%s' (%s)", self.name, obj_name, obj_type
            )
            return

        last_checksum = meta_rows.iloc[-1]["checksum"]
        current_checksum = calculate_checksum(obj.data if hasattr(obj, "data") else obj)

        if last_checksum != current_checksum:
            self.logger.error(
                "[%s] Checksum mismatch detected on load for '%s' (%s)",
                self.name,
                obj_name,
                obj_type,
            )
        else:
            self.logger.info(
                "[%s] Checksum verified on load for '%s' (%s)",
                self.name,
                obj_name,
                obj_type,
            )

    # ------------------- Wagons ------------------- #
    def save_wagon(self, name: str, wagon, overwrite: bool = False):
        if self.has_wagon(name) and not overwrite:
            self.logger.warning(
                "[%s] Wagon '%s' exists. Use overwrite=True to replace.",
                self.name,
                name,
            )
            return
        self.logger.info("[%s] Saving Wagon: %s", self.name, name)
        self.storage.save_wagon(name, wagon)
        self._record_metadata(name, "Wagon", "save", wagon)

    def load_wagon(self, name: str):
        wagon = self.storage.load_wagon(name)
        self._verify_on_load(name, "Wagon", wagon)
        return wagon

    def remove_wagon(self, name: str):
        if not self.has_wagon(name):
            self.logger.warning("[%s] Wagon '%s' does not exist.", self.name, name)
            return
        wagon = self.storage.remove_wagon(name)
        self._record_metadata(name, "Wagon", "remove", wagon)
        return wagon

    def has_wagon(self, name: str):
        return self.storage.has_wagon(name)

    # ------------------- Boxes ------------------- #
    def save_box(self, name: str, box, overwrite: bool = False):
        if self.has_box(name) and not overwrite:
            self.logger.warning(
                "[%s] Box '%s' exists. Use overwrite=True to replace.", self.name, name
            )
            return
        self.logger.info("[%s] Saving Box: %s", self.name, name)
        self.storage.save_box(name, box)
        self._record_metadata(name, "Box", "save", box)

    def load_box(self, name: str):
        box = self.storage.load_box(name)
        self._verify_on_load(name, "Box", box)
        return box

    def remove_box(self, name: str):
        if not self.has_box(name):
            self.logger.warning("[%s] Box '%s' does not exist.", self.name, name)
            return
        box = self.storage.remove_box(name)
        self._record_metadata(name, "Box", "remove", box)
        return box

    def has_box(self, name: str):
        return self.storage.has_box(name)

    # ------------------- Containers ------------------- #
    def save_container(self, name: str, container, overwrite: bool = False):
        if self.has_container(name) and not overwrite:
            self.logger.warning(
                "[%s] Container '%s' exists. Use overwrite=True to replace.",
                self.name,
                name,
            )
            return
        self.logger.info("[%s] Saving Container: %s", self.name, name)
        self.storage.save_container(name, container)
        self._record_metadata(name, "Container", "save", container)

    def load_container(self, name: str):
        container = self.storage.load_container(name)
        self._verify_on_load(name, "Container", container)
        return container

    def remove_container(self, name: str):
        if not self.has_container(name):
            self.logger.warning("[%s] Container '%s' does not exist.", self.name, name)
            return
        container = self.storage.remove_container(name)
        self._record_metadata(name, "Container", "remove", container)
        return container

    def has_container(self, name: str):
        return self.storage.has_container(name)

    # ------------------- Reporting ------------------- #
    def report(self):
        """
        Return a metadata report of all storage operations with checksums.
        """
        return self.metadata.copy()

    def __repr__(self):
        return "<StorageManager name=%s>" % self.name
