"""
In-memory store for Fragua ETL objects.
Now supports only Wagon and Box storage types.
"""

from typing import (
    Dict,
    Optional,
    Literal,
    Union,
    List,
    Mapping,
    Any,
    cast,
)
from fragua.utils.logger import get_logger
from fragua.store.storage_types import Wagon, Box

logger = get_logger(__name__)

# Only the allowed types remain
StorageType = Literal["wagon", "box"]


class Store:
    """
    In-memory store for Wagons and Boxes.
    Containers are excluded — they are higher-level composites.
    """

    VALID_STORAGE_TYPES = ("wagon", "box")

    def __init__(
        self,
        store_name: str,
        storage_types: Union[StorageType, List[StorageType], Literal["all"]] = "all",
    ) -> None:
        """
        Initialize the store with a name and allowed object types.

        Args:
            store_name (str): Identifier for this store instance.
            storage_types (str | list[str] | 'all'): Object types this store can manage.
                'all' includes all valid types ('wagon' and 'box').
        """
        self.store_name = store_name

        if storage_types == "all":
            types_to_store = list(self.VALID_STORAGE_TYPES)
        elif isinstance(storage_types, str):
            types_to_store = (
                [storage_types] if storage_types in self.VALID_STORAGE_TYPES else []
            )
        else:
            types_to_store = [t for t in storage_types if t in self.VALID_STORAGE_TYPES]
            invalid = [t for t in storage_types if t not in self.VALID_STORAGE_TYPES]
            if invalid:
                logger.warning(
                    "[%s] Ignoring invalid store types: %s",
                    self.store_name,
                    invalid,
                )

        self._store: Dict[StorageType, Dict[str, Union[Wagon, Box]]] = {
            cast(StorageType, t): {} for t in types_to_store
        }

    @property
    def store(self) -> Dict[StorageType, Dict[str, Union[Wagon, Box]]]:
        """Return the internal store mapping."""
        return self._store

    def add(
        self,
        storage_type: StorageType,
        obj: Union[Wagon, Box],
        name: Optional[str] = None,
        overwrite: bool = False,
    ) -> None:
        """Add a Wagon or Box to the store."""
        if storage_type not in self._store:
            raise ValueError(
                f"Object type '{storage_type}' is not allowed in this store."
            )

        store_name = name or getattr(obj, "name", None)
        if store_name is None:
            raise ValueError(
                "Storage object must have a 'name' attribute or provide 'name' argument."
            )

        store_name = str(store_name)

        if self.exists(storage_type, store_name) and not overwrite:
            logger.warning(
                "[%s] %s '%s' already exists. Use overwrite=True to replace.",
                self.store_name,
                storage_type,
                store_name,
            )
            return

        self._store[storage_type][store_name] = obj
        logger.debug(
            "[%s] Added %s '%s' to store",
            self.store_name,
            storage_type,
            store_name,
        )

    def get(
        self,
        storage_type: Union[StorageType, Literal["all"]] = "all",
        name: str = "all",
    ) -> Union[
        Optional[Union[Wagon, Box]],
        Mapping[str, Union[Wagon, Box]],
        Mapping[StorageType, Mapping[str, Union[Wagon, Box]]],
    ]:
        """Retrieve Wagons or Boxes from the store."""
        if storage_type == "all":
            if name != "all":
                raise ValueError("Cannot specify a single name when storage_type='all'")
            return cast(
                Mapping[StorageType, Mapping[str, Union[Wagon, Box]]],
                {t: dict(objs) for t, objs in self._store.items()},
            )

        if name == "all":
            return cast(
                Mapping[str, Union[Wagon, Box]],
                dict(self._store[storage_type]),
            )

        return self._store.get(storage_type, {}).get(name)

    def remove(
        self,
        storage_type: Union[StorageType, Literal["all"]] = "all",
        name: str = "all",
    ) -> Union[
        Optional[Union[Wagon, Box]],
        Mapping[str, Union[Wagon, Box]],
        Mapping[StorageType, Mapping[str, Union[Wagon, Box]]],
    ]:
        """Remove Wagons or Boxes from the store."""
        if storage_type == "all":
            if name != "all":
                raise ValueError("Cannot specify a single name when storage_type='all'")
            all_objs = {t: dict(objs) for t, objs in self._store.items()}
            for t in self._store.keys():
                self._store[t].clear()
            return cast(
                Mapping[StorageType, Mapping[str, Union[Wagon, Box]]],
                all_objs,
            )

        if name == "all":
            objs = dict(self._store[storage_type])
            self._store[storage_type].clear()
            return cast(Mapping[str, Union[Wagon, Box]], objs)

        return self._store.get(storage_type, {}).pop(name, None)

    def remove_all(
        self,
    ) -> Mapping[StorageType, Mapping[str, Union[Wagon, Box]]]:
        """Remove all Wagons and Boxes from the store."""
        return self.remove("all", "all")  # type: ignore

    def exists(self, storage_type: StorageType, name: str) -> bool:
        """Check if an object exists in the store."""
        return name in self._store.get(storage_type, {})

    def list_all(
        self, storage_type: Optional[StorageType] = None
    ) -> Mapping[StorageType, Mapping[str, dict[Any, Any]]]:
        """
        Return metadata of all stored Storage objects (Wagons and Boxes only).
        """
        types_to_list = [storage_type] if storage_type else list(self._store.keys())
        result: dict[StorageType, dict[str, dict[Any, Any]]] = {}

        for t in types_to_list:
            key = cast(StorageType, t)
            objs_metadata: dict[str, dict[Any, Any]] = {}
            for name, obj in self._store[key].items():
                objs_metadata[name] = getattr(obj, "metadata", {})
            result[key] = objs_metadata

        return result
