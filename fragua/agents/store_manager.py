"""
StoreManager agent for Fragua ETL.
Manages Wagons, Boxes, and Containers using in-memory Store.
Handles metadata, checksums, logging, and unified reporting.
"""

from typing import Optional, Mapping, Union, Literal, Generic, Any, Dict, List
from fragua.store.store import Store, StorageT
from fragua.utils.metrics import (
    StorageType,
    add_metadata_to_storage,
    determine_storage_type,
    generate_metadata,
)
from fragua.utils.logger import get_logger

logger = get_logger(__name__)

# -------------------- Type Aliases -------------------- #


# -------------------- StoreManager -------------------- #
class StoreManager(Generic[StorageT]):
    """Dynamic StoreManager that works with types defined in the Store."""

    def __init__(self, store: Store[StorageT], name: str = "StoreManager") -> None:
        self.name = name
        self.store = store

    # ------------------- Metadata ------------------- #
    def _generate_save_metadata(
        self, storage: StorageT, storage_name: str, agent_name: Optional[str]
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
    def save(
        self,
        storage: StorageT,
        **kwargs: Any,
    ) -> None:
        """
        Save a single object into the store, enriching its metadata
        with store manager info and agent name.

        kwargs:
            storage_name: Key name under which to store the object (required).
            agent_name: Name of the agent performing the save (optional).
            overwrite: Whether to overwrite if object already exists (optional, default False).
        """

        storage_type: StorageType = determine_storage_type(storage=storage)

        if storage_type is None:
            raise ValueError(f"Storage type '{storage_type}' is not a válid type.")

        if storage_type not in self.store.store:
            raise ValueError(
                f"Storage type '{storage_type}' is not managed by this Store."
            )

        storage_name = kwargs.get("storage_name")
        if not storage_name:
            raise ValueError("Missing required argument: 'storage_name'")

        agent_name: Optional[str] = kwargs.get("agent_name")
        overwrite: bool = kwargs.get("overwrite", False)

        if self.store.exists(storage_type, storage_name) and not overwrite:
            logger.warning(
                "[%s] %s '%s' exists. Use overwrite=True to replace.",
                self.name,
                storage_type,
                storage_name,
            )
            return

        self._generate_save_metadata(storage, storage_name, agent_name)
        self.store.add(storage_type, storage, name=storage_name, overwrite=overwrite)

        logger.info(
            "[%s] Saved %s '%s' by agent '%s'",
            self.name,
            storage_type,
            storage_name,
            agent_name,
        )

    def get(
        self,
        storage_type: StorageType | Literal["all"] = "all",
        storage_name: str = "all",
    ) -> Union[
        Optional[StorageT],
        Mapping[str, StorageT],
        Mapping[StorageType, Mapping[str, StorageT]],
    ]:
        """Retrieve objects from the store (single, all of type, or all types)."""
        return self.store.get(storage_type, storage_name)

    def remove(
        self,
        storage_type: StorageType | Literal["all"] = "all",
        storage_name: str = "all",
    ) -> Union[
        Optional[StorageT],
        Mapping[str, StorageT],
        Mapping[StorageType, Mapping[str, StorageT]],
    ]:
        """Remove storages from the store, supporting single, all of a type, or all types."""
        removed = self.store.remove(storage_type, storage_name)
        if isinstance(removed, dict):
            count = sum(len(v) if isinstance(v, dict) else 1 for v in removed.values())
            logger.info("[%s] Removed %d object(s)", self.name, count)
        elif removed:
            logger.info(
                "[%s] Removed object '%s' of type '%s'",
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
        selected_fields = None if all_fields else (fields or default_fields)

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
