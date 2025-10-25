"""
In-memory store for Fragua ETL objects.
"""

from typing import (
    Dict,
    Optional,
    Literal,
    Union,
    List,
    TypeVar,
    Generic,
    Mapping,
    Any,
    cast,
)
from fragua.core.base_storage import BaseStorage
from fragua.utils.logger import get_logger

logger = get_logger(__name__)

ObjType = Literal["wagon", "box", "container"]
StorageT = TypeVar("StorageT", bound=BaseStorage[Any])


class Store(Generic[StorageT]):
    """
    Minimal in-memory store for BaseStorage objects (wagon, box, container).
    Handles storage of one or more object types, without touching metadata.
    """

    VALID_TYPES = ("wagon", "box", "container")

    def __init__(
        self,
        store_name: str,
        store_types: Union[
            Literal["wagon", "box", "container", "all"], List[str]
        ] = "all",
    ) -> None:
        """
        Initialize the store with a name and allowed object types.

        Args:
            store_name (str): Identifier for this store instance.
            store_types (str | List[str]): Object types this store can manage.
                'all' includes all valid types.
        """
        self.store_name = store_name

        if store_types == "all":
            types_to_store = list(self.VALID_TYPES)
        elif isinstance(store_types, str):
            types_to_store = [store_types] if store_types in self.VALID_TYPES else []
        else:
            types_to_store = [t for t in store_types if t in self.VALID_TYPES]
            invalid = [t for t in store_types if t not in self.VALID_TYPES]
            if invalid:
                logger.warning(
                    "[%s] Ignoring invalid store types: %s",
                    self.store_name,
                    invalid,
                )

        self._store: Dict[str, Dict[str, StorageT]] = {t: {} for t in types_to_store}

    @property
    def store(self) -> Dict[str, Dict[str, StorageT]]:
        """Get store."""
        return self._store

    # ------------------- Store Operations ------------------- #

    def add(
        self,
        obj_type: ObjType,
        obj: StorageT,
        name: Optional[str] = None,
        overwrite: bool = False,
    ) -> None:
        """
        Add a BaseStorage object to the store without modifying its metadata.
        Ensures the store key is always a string.

        Args:
            obj_type (ObjType): Type of the object ('wagon', 'box', 'container').
            obj (BaseStorage): The object to store.
            name (str, optional): Name under which to store the object. Defaults to obj.name.
            overwrite (bool): If True, overwrite existing object with same name.
        """
        if obj_type not in self._store:
            raise ValueError(f"Object type '{obj_type}' is not allowed in this store.")

        # Determine the key name
        store_name = name or getattr(obj, "name", None)
        if store_name is None:
            raise ValueError(
                "Storage object must have a 'name' attribute or provide 'name' argument."
            )

        # Ensure it's a string
        if not isinstance(store_name, str):
            store_name = str(store_name)

        # Check for existing object
        if self.exists(obj_type, store_name) and not overwrite:
            logger.warning(
                "[%s] %s '%s' already exists. Use overwrite=True to replace.",
                self.store_name,
                obj_type,
                store_name,
            )
            return

        # Add the object
        self._store[obj_type][store_name] = obj
        logger.debug(
            "[%s] Added %s '%s' to store", self.store_name, obj_type, store_name
        )

    def get(
        self, obj_type: Union[ObjType, Literal["all"]] = "all", name: str = "all"
    ) -> Union[
        Optional[StorageT],
        Mapping[str, StorageT],
        Mapping[ObjType, Mapping[str, StorageT]],
    ]:
        """Retrieve objects from the store."""
        if obj_type == "all":
            if name != "all":
                raise ValueError("Cannot specify a single name when obj_type='all'")
            return cast(
                Mapping[ObjType, Mapping[str, StorageT]],
                {t: dict(objs) for t, objs in self._store.items()},
            )

        if name == "all":
            return cast(Mapping[str, StorageT], dict(self._store[obj_type]))

        return self._store.get(obj_type, {}).get(name)

    def remove(
        self, obj_type: Union[ObjType, Literal["all"]] = "all", name: str = "all"
    ) -> Union[
        Optional[StorageT],
        Mapping[str, StorageT],
        Mapping[ObjType, Mapping[str, StorageT]],
    ]:
        """Remove objects from the store."""
        if obj_type == "all":
            if name != "all":
                raise ValueError("Cannot specify a single name when obj_type='all'")
            all_objs = {t: dict(objs) for t, objs in self._store.items()}
            for t in self._store.keys():
                self._store[t].clear()
            return cast(Mapping[ObjType, Mapping[str, StorageT]], all_objs)

        if name == "all":
            objs = dict(self._store[obj_type])
            self._store[obj_type].clear()
            return cast(Mapping[str, StorageT], objs)

        return self._store.get(obj_type, {}).pop(name, None)

    def remove_all(self) -> Mapping[ObjType, Mapping[str, StorageT]]:
        """Remove all objects from the store."""
        return self.remove("all", "all")  # type: ignore

    def exists(self, obj_type: ObjType, name: str) -> bool:
        """Check if an object exists in the store."""
        return name in self._store.get(obj_type, {})

    def list_all(
        self, obj_type: Optional[ObjType] = None
    ) -> Mapping[ObjType, Mapping[str, dict[Any, Any]]]:
        """
        Return metadata of all stored BaseStorage objects.
        """
        types_to_list = [obj_type] if obj_type else self._store.keys()
        result: dict[str, dict[str, dict[Any, Any]]] = {}

        for t in types_to_list:
            objs_metadata: dict[str, dict[Any, Any]] = {}
            for name, obj in self._store[t].items():
                # name ya es str
                if hasattr(obj, "metadata") and isinstance(obj.metadata, dict):
                    objs_metadata[name] = obj.metadata
                else:
                    objs_metadata[name] = {}
            result[t] = objs_metadata

        return cast(Mapping[ObjType, Mapping[str, dict[Any, Any]]], result)
