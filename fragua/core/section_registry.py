"""Section Registry class."""

from abc import ABC
from typing import Any, Dict, Optional

from fragua.core.entry_section import EntrySection


class SectionRegistry(ABC):
    """Section registry class."""

    def __init__(self, section_name: str):
        """Initialize section registry."""
        self.section_name = section_name
        self._entries: Dict[str, EntrySection] = {}

    # ---------------------------------------------------------
    # Validation helpers
    # ---------------------------------------------------------

    def _exists(self, key: str) -> bool:
        """Return True if the entry exists."""
        return key in self._entries

    def _not_exists(self, key: str) -> bool:
        """Return True if the entry does not exist."""
        return key not in self._entries

    # ---------------------------------------------------------
    # CRUD operations
    # ---------------------------------------------------------

    def create_entry(self, name: str, component: Any) -> bool:
        """Create an entry linked to a component."""

        if self._not_exists(name):
            self._entries[name] = EntrySection(name, component)
            return True
        return False

    def get_entry(self, name: str) -> Optional[EntrySection]:
        """Retrieve a specific entry."""
        return self._entries.get(name)

    def get_entries(self) -> Dict[str, EntrySection]:
        """Retrieve all entries."""
        return self._entries

    def update_entry(self, old_name: str, new_name: str) -> bool:
        """
        Rename an entry.
        """
        if self._exists(old_name) and self._not_exists(new_name):
            entry = self._entries.pop(old_name)
            entry.name = new_name
            self._entries[new_name] = entry
            return True
        return False

    def delete_entry(self, name: str) -> bool:
        """Delete an entry."""
        return self._entries.pop(name, None) is not None
