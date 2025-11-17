"""
WarehouseManager class in Fragua.
Handles all logic for adding, getting, removing, and listing storages.
"""

from typing import Any, TypeAlias, Union, Optional, Mapping, Dict, List, Literal
from datetime import datetime
import copy as py_copy

from fragua.storages.storage import Storage
from fragua.utils.logger import get_logger

from fragua.storages.warehouse import Warehouse
from fragua.storages.storage_types import Box, STORAGE_CLASSES

logger = get_logger(__name__)

StorageType = Literal["box", "all"]
StorageResult: TypeAlias = Union[
    Box,
    Storage[Box],
    Mapping[str, Storage[Box]],
    Mapping[str, Mapping[str, Storage[Box]]],
]


class WarehouseManager:
    """
    Encapsulates storage management logic for Box objects in a flat Warehouse structure.
    Provides add, get, delete, rename, copy, batch operations,
    metadata search, snapshot, and undo capabilities.
    """

    def __init__(self, name: str, warehouse: Warehouse) -> None:
        self.warehouse = warehouse
        self.name = name
        self._movement_log: List[dict[str, object]] = []
        self._undo_stack: List[dict[str, Any]] = []

    def summary(self) -> Dict[str, Any]:
        """
        Return a JSON-serializable summary of the WarehouseManager state.

        Includes:
            - manager name
            - warehouse name
            - number of storages
            - storage names and their types
            - full movement log
            - counters (log size, undo size)
        """
        warehouse_name = getattr(self.warehouse, "warehouse_name", None)

        # Map each storage name to its class name
        storages_info: Dict[str, str] = {
            name: obj.__class__.__name__ for name, obj in self.warehouse.data.items()
        }

        return {
            "manager_name": self.name,
            "warehouse_name": warehouse_name,
            "storage_count": len(self.warehouse.data),
            "storages": storages_info,
            "movement_log": self._movement_log.copy(),
            "log_entries": len(self._movement_log),
            "undo_stack_size": len(self._undo_stack),
        }

    # ------------------- Movement Logging ------------------- #
    def _log_movement(self, /, **movement_log: Any) -> None:
        """Records a movement in the internal log."""
        now = datetime.now().astimezone()
        date_str = now.date().isoformat()
        time_str = now.time().strftime("%H:%M:%S")
        raw_offset = now.strftime("%z")
        tz_offset = (
            f"{raw_offset[:3]}:{raw_offset[3:]}"
            if raw_offset and len(raw_offset) == 5
            else raw_offset or ""
        )
        entry: dict[str, object] = {
            "date": date_str,
            "time": time_str,
            "timezone": tz_offset,
            "operation": movement_log.get("operation"),
            "storage_name": movement_log.get("storage_name"),
            "agent_name": movement_log.get("agent_name"),
            "warehouse": getattr(self.warehouse, "warehouse_name", None),
            "success": movement_log.get("success"),
            "details": movement_log.get("details") or {},
        }
        self._movement_log.append(entry)
        logger.info(
            "[%s] Movement logged by '%s': %s '%s' by agent '%s' at %s %s %s",
            self.name,
            self.name,
            movement_log.get("operation"),
            movement_log.get("storage_name"),
            movement_log.get("agent_name"),
            entry["date"],
            entry["time"],
            entry["timezone"],
        )

    def get_movements_log(self) -> List[dict[str, object]]:
        """
        Return a copy of the movements log.

        Returns:
            List[dict[str, object]]: List of movement entries.
        """
        return self._movement_log.copy()

    # ----------------------------- Add ----------------------------- #
    def add(
        self,
        storage: Storage[Box],
        storage_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        overwrite: bool = False,
    ) -> None:
        """Add a Box to the Warehouse with logging and undo support."""
        storage_type = storage.__class__.__name__.lower()
        try:
            if storage_name is None:
                raise ValueError("Missing required argument: 'storage_name'")
            if storage_type != "box":
                raise ValueError(f"Invalid storage_type '{storage_type}'")

            old_obj = self.warehouse.data.get(storage_name)
            if old_obj and not overwrite:
                self._log_movement(
                    operation="add",
                    storage_type=storage_type,
                    storage_name=storage_name,
                    agent_name=agent_name,
                    success=False,
                    details={"reason": "exists"},
                )
                return

            # Backup for undo
            if old_obj:
                self._undo_stack.append(
                    {
                        "operation": "add",
                        "name": storage_name,
                        "backup": py_copy.deepcopy(old_obj),
                    }
                )
            else:
                self._undo_stack.append(
                    {"operation": "add", "name": storage_name, "backup": None}
                )

            self.warehouse.data[storage_name] = storage
            self._log_movement(
                operation="add",
                storage_type=storage_type,
                storage_name=storage_name,
                agent_name=agent_name,
                success=True,
            )
        except Exception as e:
            self._log_movement(
                operation="add",
                storage_type=storage_type,
                storage_name=storage_name or "unknown",
                agent_name=agent_name,
                success=False,
                details={"error": str(e)},
            )
            raise

    # ----------------------------- Get Helpers ----------------------------- #
    def _get_one(
        self, storage_name: str, storage_type: StorageType
    ) -> Optional[Storage[Box]]:
        classes = Box if storage_type == "all" else STORAGE_CLASSES[storage_type]
        obj = self.warehouse.data.get(storage_name)
        return obj if isinstance(obj, classes) else None

    def _get_all(self, storage_type: StorageType) -> Dict[str, Storage[Box]]:
        classes = Box if storage_type == "all" else STORAGE_CLASSES[storage_type]
        return {
            name: obj
            for name, obj in self.warehouse.data.items()
            if isinstance(obj, classes)
        }

    def get(
        self,
        agent_name: str,
        storage_type: StorageType = "all",
        storage_name: str = "all",
    ) -> Optional[StorageResult]:
        """Pipeline method for getting storage objects."""
        try:
            if storage_name != "all":
                # Single object or None
                result: Optional[Storage[Box]] = self._get_one(
                    storage_name, storage_type
                )
            else:
                # Dict of objects
                result_dict: Dict[str, Storage[Box]] = self._get_all(storage_type)
                result = result_dict  # type: ignore

            self._log_movement(
                operation="get",
                storage_type=storage_type,
                storage_name=storage_name,
                agent_name=agent_name,
                success=True,
                details={"result_type": type(result).__name__},
            )
            return result
        except Exception as e:
            self._log_movement(
                operation="get",
                storage_type=storage_type,
                storage_name=storage_name,
                agent_name=agent_name,
                success=False,
                details={"error": str(e)},
            )
            raise

    # ----------------------------- Delete Helpers ----------------------------- #
    def _delete_one(
        self, storage_name: str, storage_type: StorageType
    ) -> Optional[Storage[Box]]:
        obj = self._get_one(storage_name, storage_type)
        if obj:
            self._undo_stack.append(
                {
                    "operation": "delete",
                    "name": storage_name,
                    "backup": py_copy.deepcopy(obj),
                }
            )
            del self.warehouse.data[storage_name]
        return obj

    def _delete_multiple(self, storage_type: StorageType) -> Dict[str, Storage[Box]]:
        classes = Box if storage_type == "all" else STORAGE_CLASSES[storage_type]
        to_delete = {
            name: obj
            for name, obj in self.warehouse.data.items()
            if isinstance(obj, classes)
        }
        for name, obj in to_delete.items():
            self._undo_stack.append(
                {"operation": "delete", "name": name, "backup": py_copy.deepcopy(obj)}
            )
            del self.warehouse.data[name]
        return to_delete

    def delete(
        self, storage_type: StorageType, storage_name: str = "all"
    ) -> Union[Optional[Storage[Box]], Dict[str, Storage[Box]]]:
        """Pipeline method for deleting storage objects with undo support."""
        try:
            if storage_name != "all":
                removed: Optional[Storage[Box]] = self._delete_one(
                    storage_name, storage_type
                )
                count_removed = 1 if removed else 0
            else:
                removed_dict: Dict[str, Storage[Box]] = self._delete_multiple(
                    storage_type
                )
                removed = removed_dict  # type: ignore
                count_removed = len(removed_dict)

            self._log_movement(
                operation="delete",
                storage_type=storage_type,
                storage_name=storage_name,
                agent_name=None,
                success=bool(count_removed),
                details={"removed_count": count_removed},
            )
            return removed
        except Exception as e:
            self._log_movement(
                operation="delete",
                storage_type=storage_type,
                storage_name=storage_name,
                agent_name=None,
                success=False,
                details={"error": str(e)},
            )
            raise

    # ----------------------------- Additional Functionalities ----------------------------- #
    def rename(self, old_name: str, new_name: str) -> bool:
        """Rename a storage object if it exists."""
        if old_name not in self.warehouse.data or new_name in self.warehouse.data:
            return False
        self.warehouse.data[new_name] = self.warehouse.data.pop(old_name)
        self._log_movement(
            operation="rename",
            storage_type="box",
            storage_name=new_name,
            agent_name=None,
            success=True,
            details={"from": old_name, "to": new_name},
        )
        return True

    def copy(self, storage_name: str, new_name: str) -> bool:
        """Duplicate a storage object if it exists and new_name is free."""
        obj = self.warehouse.data.get(storage_name)
        if not obj or new_name in self.warehouse.data:
            return False
        self.warehouse.data[new_name] = py_copy.deepcopy(obj)
        self._log_movement(
            operation="copy",
            storage_type="box",
            storage_name=new_name,
            agent_name=None,
            success=True,
            details={"from": storage_name},
        )
        return True

    def batch_add(
        self, items: Dict[str, Storage[Box]], overwrite: bool = False
    ) -> None:
        """Add multiple storage objects at once."""
        for name, obj in items.items():
            self.add(obj, storage_name=name, overwrite=overwrite)

    def search_by_metadata(self, key: str, value: Any) -> Dict[str, Storage[Box]]:
        """Search objects by metadata key/value."""
        return {
            name: obj
            for name, obj in self.warehouse.data.items()
            if getattr(obj, "metadata", {}).get(key) == value
        }

    def snapshot(self) -> Dict[str, Storage[Box]]:
        """Return a shallow copy of the warehouse state."""
        return self.warehouse.data.copy()

    def undo_last_action(self) -> bool:
        """Undo the last add or delete action."""
        if not self._undo_stack:
            return False
        last = self._undo_stack.pop()
        op, name, backup = last["operation"], last["name"], last["backup"]
        if op == "add":
            if backup:
                self.warehouse.data[name] = backup
            else:
                self.warehouse.data.pop(name, None)
        elif op == "delete" and backup:
            self.warehouse.data[name] = backup
        self._log_movement(
            operation="undo",
            storage_type="box",
            storage_name=name,
            agent_name=None,
            success=True,
            details={"reverted_operation": op},
        )
        return True
