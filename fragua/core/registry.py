"""Base class for all registries of an environment in Fragua."""

from typing import Any, Dict, List, Optional


ACTION_TYPES: List[str] = ["extract", "transform", "load"]


class Registry:
    """Configuration class for all registries types of an environment."""

    def __init__(
        self, name: str, entries: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> None:
        """Initialize the registry."""
        self.name: str = name
        self._entries: Dict[str, Dict[str, Any]] = (
            {atype: {} for atype in ACTION_TYPES} if entries is None else entries
        )

    def _check_entrie_name(self, name: str) -> bool:
        """Ensure no entrie in the registry already has the given name."""
        return not any(name in entries for entries in self._entries.values())

    def _check_action_type(self, action: str) -> bool:
        """Check if the action type is valid."""
        return action in ACTION_TYPES

    def _validate_entrie(
        self,
        action: Optional[str],
        entrie_name: str,
        not_exist_name: bool = False,
    ) -> bool:
        """
        Validate entry existence.
        If action is provided, validate only inside that action.
        If action is None, validate across all actions.
        """
        if action is not None:
            if not self._check_action_type(action):
                return False
            exists = entrie_name in self._entries[action]
        else:
            exists = any(entrie_name in entries for entries in self._entries.values())

        return not exists if not_exist_name else exists

    def set_entries(self, entries: Dict[str, Dict[str, Any]]) -> None:
        """Set or replace all registry entries."""
        self._entries = entries

    def get_entries(self, action: Optional[str] = "all") -> Dict[str, Any]:
        """
        Retrieve registry entries.

        - action="all" (default): return full structure {action: {name: entrie}}
        - action=None: return merged entries {name: entrie}
        - action="<action>": return entries of a single action
        """

        if action == "all":
            return self._entries

        if action is None:
            merged = {}
            for entries in self._entries.values():
                merged.update(entries)
            return merged

        if action in ACTION_TYPES:
            return self._entries[action]

        return {}

    def create_entrie(self, action: Optional[str], name: str, new_entrie: Any) -> bool:
        """
        Create a new entry.
        If action is None → cannot determine target action → return False.
        """
        if action is None or not self._check_action_type(action):
            return False

        created = self._validate_entrie(action, name, not_exist_name=True)

        if created:
            self._entries[action][name] = new_entrie

        return created

    def get_entrie(
        self,
        name: str,
        action: Optional[str],
    ) -> Any | None:
        """
        Retrieve an entry by name.
        - If `action` is provided, search only within that action.
        - If `action` is None, search across all actions.
        """
        if action is not None and self._check_action_type(action):
            return (
                self._entries[action].get(name)
                if self._validate_entrie(action, name)
                else None
            )

        for _, entries in self._entries.items():
            if name in entries:
                return entries[name]

        return None

    def update_entrie(self, action: Optional[str], name: str, new_name: str) -> bool:
        """
        Update an entrie.
        If action is None → search the entry in all actions.
        """
        if action is None:
            action = next(
                (act for act, ents in self._entries.items() if name in ents), None
            )
            if action is None:
                return False

        exist_entrie = self._validate_entrie(action, name)
        valid_new_name = self._validate_entrie(action, new_name, not_exist_name=True)

        updated = exist_entrie and valid_new_name

        if updated:
            setattr(self._entries[action][name], "name", new_name)
            self._entries[action][new_name] = self._entries[action].pop(name)

        return updated

    def delete_entrie(self, action: Optional[str], name: str) -> bool:
        """
        Delete an entrie.
        If action is None → search in all actions.
        """
        if action is None:
            action = next(
                (act for act, ents in self._entries.items() if name in ents), None
            )
            if action is None:
                return False

        deleted = self._validate_entrie(action, name)

        if deleted:
            self._entries[action].pop(name)

        return deleted

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"
