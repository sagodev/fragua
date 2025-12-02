"""Base class for all registries of an environment in Fragua."""

from typing import Any, Dict, Optional
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Registry:
    """Configuration class for all registries types of an environment."""

    def __init__(
        self, name: str, entries: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> None:
        """Initialize the registry."""
        self.name: str = name
        self._entries: Dict[str, Dict[str, Any]] = {} if entries is None else entries

    def _check_entrie_name(self, name: str) -> bool:
        """Ensure no entrie in the registry already has the given name."""
        return not any(name in entries for entries in self._entries.values())

    def _validate_entrie(
        self,
        record_name: str,
        not_exist_name: bool = False,
    ) -> bool:
        """Check if a registry is valid."""

        exist_name = self._check_entrie_name(record_name)

        is_valid_name = exist_name if not_exist_name else not exist_name

        is_valid_registry = is_valid_name

        return is_valid_registry

    def set_entries(self, entries: Dict[str, Dict[str, Any]]) -> None:
        """Set or replace all registry entries."""
        self._entries = entries

    def get_entries(self) -> Dict[str, Dict[str, Any]]:
        """Retrive all registry entries."""
        return self._entries

    def create_entrie(self, action: str, name: str, new_entrie: Dict[str, Any]) -> bool:
        """
        Create a new entrie in registry.
        Return boolean if entrie is created succesfully or not.
        """
        created = self._validate_entrie(name, not_exist_name=True)

        if created:
            self._entries[action][name] = new_entrie
            logger.info("%s created: %s", self.name.capitalize(), name)

        return created

    def get_entrie(
        self,
        action: str,
        name: str,
    ) -> Any | None:
        """
        Retrieve a record from a registry by name.
        If entrie is not in registry return None.
        """

        record = (
            self._entries[action].get(name) if self._validate_entrie(name) else None
        )

        return record

    def update_entrie(
        self, action: str, name: str, updated_entrie: Dict[str, Any]
    ) -> bool:
        """
        Update an existing record in a registry.
        Return boolean if record is updated succesfully or not.
        """

        updated = self._validate_entrie(name)

        if updated:
            self._entries[action].update(updated_entrie)
            logger.info("%s updated: %s", self.name.capitalize(), name)

        return updated

    def delete_entrie(self, action: str, name: str) -> bool:
        """
        Delete a record from a registry by name.
        Return boolean if record is created succesfully or not.
        """

        deleted = self._validate_entrie(name)

        if deleted:
            self._entries[action].pop(name)
            logger.info("%s deleted: %s", self.name.capitalize(), name)

        return deleted

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}')"
