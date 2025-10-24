"""
StoreManager agent for Fragua ETL.
Manages Wagons, Boxes, and Containers using in-memory Store.
Handles metadata, checksums, logging, and unified reporting.
"""

from typing import Optional, Mapping, cast, Any, Union, Literal, Generic

from fragua.store.store import Store, StorageT, ObjType
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

    def _generate_save_metadata(self, obj: StorageT, agent_name: Optional[str]) -> None:
        metadata = generate_metadata(
            obj,
            metadata_type="save",
            agent_name=agent_name,
            store_manager_name=self.name,
        )
        add_metadata_to_storage(obj, metadata)

    # ------------------- Store Operations ------------------- #
    def save(
        self,
        obj_type: ObjType,
        obj: StorageT,
        name: Optional[str] = None,
        agent_name: Optional[str] = None,
        overwrite: bool = False,
    ) -> None:
        """
        Save a single object into the store, enriching its metadata
        with store manager info and agent name.
        """
        store_name = name or getattr(obj, "name", None)
        if store_name is None:
            raise ValueError("Object must have a name or provide 'name' argument.")

        if self.store.exists(obj_type, store_name) and not overwrite:
            logger.warning(
                "[%s] %s '%s' exists. Use overwrite=True to replace.",
                self.name,
                obj_type,
                store_name,
            )
            return

        self._generate_save_metadata(obj, agent_name)

        # Corregido: obj va en segundo lugar
        self.store.add(obj_type, obj, store_name, overwrite=overwrite)

        logger.info(
            "[%s] Saved %s '%s' by agent '%s'",
            self.name,
            obj_type,
            store_name,
            agent_name,
        )

    def get(
        self, obj_type: Union[ObjType, Literal["all"]] = "all", name: str = "all"
    ) -> Union[
        Optional[StorageT],
        Mapping[str, StorageT],
        Mapping[ObjType, Mapping[str, StorageT]],
    ]:
        """Retrieve objects from the store (single, all of type, or all types)."""
        return self.store.get(obj_type, name)

    def remove(
        self, obj_type: Union[ObjType, Literal["all"]] = "all", name: str = "all"
    ) -> Union[
        Optional[StorageT],
        Mapping[str, StorageT],
        Mapping[ObjType, Mapping[str, StorageT]],
    ]:
        """Remove objects from the store, supporting single, all of a type, or all types."""
        removed = self.store.remove(obj_type, name)
        if isinstance(removed, dict):
            count = sum(len(v) if isinstance(v, dict) else 1 for v in removed.values())
            logger.info("[%s] Removed %d object(s)", self.name, count)
        elif removed:
            logger.info(
                "[%s] Removed object '%s' of type '%s'", self.name, name, obj_type
            )
        else:
            logger.warning(
                "[%s] Nothing removed for '%s' (%s)", self.name, name, obj_type
            )
        return removed

    def exists(self, obj_type: ObjType, name: str) -> bool:
        """Check existence of a specific object."""
        return self.store.exists(obj_type, name)

    def list_all(
        self, obj_type: Optional[ObjType] = None
    ) -> Mapping[ObjType, Mapping[str, dict[str, object]]]:
        """
        Return metadata for all stored objects, optionally filtered by type.

        Args:
            obj_type: Filter by object type. If None, return all types.

        Returns:
            Dictionary of type -> object name -> metadata.
        """
        return self.store.list_all(obj_type)

    def __repr__(self) -> str:
        """String representation of the StoreManager."""
        return f"<StoreManager name={self.name}>"
