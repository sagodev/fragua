"""
StoreManager agent for Fragua ETL.
Manages Wagons, Boxes, and Containers using in-memory Store.
Handles metadata, checksums, logging, and unified reporting.
"""

from typing import Optional, Mapping, Union, Literal, Generic, Any, Dict
from fragua.store.store import Store, StorageT
from fragua.utils.metrics import (
    add_metadata_to_storage,
    generate_metadata,
)
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class StoreManager(Generic[StorageT]):
    """Dynamic StoreManager that works with types defined in the Store."""

    def __init__(self, store: Store[StorageT], name: str = "StoreManager") -> None:
        self.name = name
        self.store = store

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
        storage_type: str,
        storage: StorageT,
        storage_name: str,
        agent_name: Optional[str] = None,
        overwrite: bool = False,
    ) -> None:
        """
        Save a single object into the store, enriching its metadata
        with store manager info and agent name.

        Args:
            storage_type: Type of the storage ('wagon', 'box', or 'container').
            storage: Storage object to save.
            name: Key name under which to store the object.
            agent_name: Name of the agent performing the save.
            overwrite: Whether to overwrite if object already exists.
        """
        if storage_type not in self.store.store:
            raise ValueError(
                f"Storage type '{storage_type}' is not managed by this Store."
            )

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
        storage_type: Union[str, Literal["all"]] = "all",
        storage_name: str = "all",
    ) -> Union[
        Optional[StorageT],
        Mapping[str, StorageT],
        Mapping[str, Mapping[str, StorageT]],
    ]:
        """Retrieve objects from the store (single, all of type, or all types)."""
        return self.store.get(storage_type, storage_name)

    def remove(
        self,
        storage_type: Union[str, Literal["all"]] = "all",
        storage_name: str = "all",
    ) -> Union[
        Optional[StorageT],
        Mapping[str, StorageT],
        Mapping[str, Mapping[str, StorageT]],
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

    def exists(self, storage_type: str, storage_name: str) -> bool:
        """Check existence of a specific object."""
        return self.store.exists(storage_type, storage_name)

    def list_all(
        self,
        storage_type: Optional[str] = None,
        fields: Optional[list[str]] = None,
        all_fields: bool = False,
    ) -> Mapping[str, Mapping[str, dict[str, object]]]:
        """
        Return filtered metadata for stored objects, optionally filtered by type.

        Args:
            storage_type: Filter by storage type. If None, return all types.
            fields: Specific metadata keys to include. Ignored if all_fields=True.
            all_fields: If True, include the full metadata of each object.

        Returns:
            Dictionary of type -> storage name -> metadata.
        """
        default_fields = ["storage_name", "type", "rows", "columns", "checksum"]
        selected_fields = None if all_fields else (fields or default_fields)

        full_metadata = self.store.list_all(storage_type)
        filtered_list: dict[str, dict[str, dict[str, object]]] = {}

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
