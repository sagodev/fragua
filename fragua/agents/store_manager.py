"""
StoreManager agent for Fragua ETL.
Manages Wagons, Boxes, and Containers using in-memory Store.
Handles metadata, checksums, logging, and unified reporting.
"""

from datetime import datetime
from typing import Optional, Mapping, Union, Literal, Any, Dict, List
from fragua.core.base_storage import BaseStorage
from fragua.store import Store
from fragua.utils.metrics import (
    StorageType,
    add_metadata_to_storage,
    determine_storage_type,
    generate_metadata,
)
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


# -------------------- StoreManager -------------------- #
class StoreManager:
    """Dynamic StoreManager that works with types defined in the Store."""

    def __init__(self, store: Store, name: str = "StoreManager") -> None:
        self.name = name
        self.store = store
        self._movement_log: List[dict[str, object]] = []

    # ------------------- Movement Logging ------------------- #
    def _log_movement(
        self,
        **movement_log: Any,
    ) -> None:
        """Records a movement in the internal log."""

        now = datetime.now().astimezone()

        date_str = now.date().isoformat()
        time_str = now.time().strftime("%H:%M:%S")

        raw_offset = now.strftime("%z")
        if raw_offset and len(raw_offset) == 5:
            tz_offset = f"{raw_offset[:3]}:{raw_offset[3:]}"
        else:
            tz_offset = raw_offset or ""

        entry: dict[str, object] = {
            "date": date_str,
            "time": time_str,
            "timezone": tz_offset,
            "operation": movement_log.get("operation"),
            "storage_type": movement_log.get("storage_type"),
            "storage_name": movement_log.get("storage_name"),
            "agent_name": movement_log.get("agent_name"),
            "store_name": self.store.store_name,
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

    def movements_log(
        self,
        storage_type: Optional[StorageType] = None,
        storage_name: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> List[dict[str, object]]:
        """Returns movements filtered by type, object name or agent."""
        result = self._movement_log
        if storage_type:
            result = [m for m in result if m["storage_type"] == storage_type]
        if storage_name:
            result = [m for m in result if m["storage_name"] == storage_name]
        if agent_name:
            result = [m for m in result if m["agent_name"] == agent_name]
        return result

    # ------------------- Metadata ------------------- #
    def _generate_save_metadata(
        self, storage: BaseStorage[Any], storage_name: str, agent_name: Optional[str]
    ) -> None:
        """Generate and attach metadata to a storage object before saving."""
        metadata_kwargs: Dict[str, Any] = {
            "metadata_type": "save",
            "storage_name": storage_name,
            "agent_name": agent_name,
            "store_manager_name": self.name,
        }
        metadata = generate_metadata(storage, **metadata_kwargs)
        add_metadata_to_storage(storage, metadata)

    # ------------------- Store Operations ------------------- #
    def save(self, storage: BaseStorage[Any], **kwargs: Any) -> None:
        """Save a storage object in the store and update movement log."""
        storage_type: StorageType | None = determine_storage_type(storage=storage)
        storage_name = kwargs.get("storage_name")
        agent_name: Optional[str] = kwargs.get("agent_name")
        overwrite: bool = kwargs.get("overwrite", False)
        movement_log: Dict[str, Any] = {}

        try:
            if storage_type is None or storage_type not in self.store.store:
                raise ValueError(
                    f"Storage type '{storage_type}' not managed by this Store."
                )

            if not storage_name:
                raise ValueError("Missing required argument: 'storage_name'")

            if self.store.exists(storage_type, storage_name) and not overwrite:
                logger.warning(
                    "[%s] %s '%s' exists. Use overwrite=True to replace.",
                    self.name,
                    storage_type,
                    storage_name,
                )

                movement_log = {
                    "operation": "save",
                    "storage_type": storage_type,
                    "storage_name": storage_name,
                    "agent_name": agent_name,
                    "success": False,
                    " details": {"reason": "exists"},
                }
                self._log_movement(**movement_log)
                return

            self._generate_save_metadata(storage, storage_name, agent_name)

            self.store.add(
                storage_type, storage, name=storage_name, overwrite=overwrite
            )

            logger.info(
                "[%s] Saved %s '%s' by agent '%s'",
                self.name,
                storage_type,
                storage_name,
                agent_name,
            )

            movement_log = {
                "operation": "save",
                "storage_type": storage_type,
                "storage_name": storage_name,
                "agent_name": agent_name,
                "success": True,
            }
            self._log_movement(**movement_log)

        except Exception as e:
            movement_log = {
                "operation": "save",
                "storage_type": storage_type,
                "storage_name": storage_name or "unknown",
                "agent_name": agent_name,
                "success": False,
                " details": {"error": str(e)},
            }
            self._log_movement(**movement_log)
            raise

    def get(
        self,
        storage_type: StorageType | Literal["all"] = "all",
        storage_name: str = "all",
    ) -> Union[
        Optional[BaseStorage[Any]],
        Mapping[str, BaseStorage[Any]],
        Mapping[StorageType, Mapping[str, BaseStorage[Any]]],
    ]:
        """Retrieve objects from the store and log the operation."""
        movement_log: Dict[str, Any] = {}
        try:
            result = self.store.get(storage_type, storage_name)
            movement_log = {
                "operation": "get",
                "storage_type": storage_type if storage_type != "all" else "all",
                "storage_name": storage_name,
                "agent_name": None,
                "success": True,
                " details": {"result_type": type(result).__name__},
            }
            self._log_movement(**movement_log)
            return result
        except Exception as e:
            movement_log = {
                "operation": "get",
                "storage_type": storage_type if storage_type != "all" else "all",
                "storage_name": storage_name,
                "agent_name": None,
                "success": False,
                " details": {"error": str(e)},
            }
            self._log_movement(**movement_log)
            raise

    def remove(
        self,
        storage_type: StorageType | Literal["all"] = "all",
        storage_name: str = "all",
    ) -> Union[
        Optional[BaseStorage[Any]],
        Mapping[str, BaseStorage[Any]],
        Mapping[StorageType, Mapping[str, BaseStorage[Any]]],
    ]:
        """Remove storages from the store and log the operation."""
        try:
            removed = self.store.remove(storage_type, storage_name)
            success = bool(removed)
            details: dict[str, object] = {}
            movement_log: Dict[str, Any] = {}

            if isinstance(removed, dict):
                count = sum(
                    len(v) if isinstance(v, dict) else 1 for v in removed.values()
                )
                details["removed_count"] = count
            elif removed:
                details["removed_count"] = 1
            else:
                details["removed_count"] = 0

            movement_log = {
                "operation": "remove",
                "storage_type": storage_type,
                "storage_name": storage_name,
                "agent_name": None,
                "success": success,
                " details": details,
            }
            self._log_movement(**movement_log)

            if success:
                logger.info(
                    "[%s] Removed object(s) '%s' of type '%s'",
                    self.name,
                    storage_name,
                    storage_type,
                )
            else:
                logger.warning(
                    "[%s] Nothing removed for '%s' (%s)",
                    self.name,
                    storage_name,
                    storage_type,
                )
            return removed
        except Exception as e:
            movement_log = {
                "operation": "remove",
                "storage_type": storage_type,
                "storage_name": storage_name,
                "agent_name": None,
                "success": False,
                " details": {"error": str(e)},
            }
            self._log_movement(**movement_log)
            raise

    def exists(self, storage_type: StorageType, storage_name: str) -> bool:
        """Check existence of a specific object."""
        return self.store.exists(storage_type, storage_name)

    def list_all(
        self,
        storage_type: Optional[StorageType] = None,
        fields: Optional[List[str]] = None,
        all_fields: bool = False,
    ) -> Mapping[StorageType, Mapping[str, dict[str, object]]]:
        """
        Return filtered metadata for stored objects, optionally filtered by type.
        """
        default_fields = ["storage_name", "type", "rows", "columns", "checksum"]
        selected_fields = [] if all_fields else (fields or default_fields)

        full_metadata = self.store.list_all(storage_type)
        filtered_list: dict[StorageType, dict[str, dict[str, object]]] = {}

        for t, storages in full_metadata.items():
            filtered_storages: dict[str, dict[str, object]] = {}
            for name, metadata in storages.items():
                if all_fields:
                    filtered_storages[name] = metadata
                else:
                    filtered_storages[name] = {
                        k: v for k, v in metadata.items() if k in selected_fields
                    }
            filtered_list[t] = filtered_storages

        return filtered_list

    def __repr__(self) -> str:
        """String representation of the StoreManager."""
        return f"<StoreManager name={self.name}>"
