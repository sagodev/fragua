"""Base class for all registries of an environment in Fragua."""

from abc import abstractmethod
from typing import Any, Dict, Optional

from fragua.core.component import FraguaComponent
from fragua.core.section_registry import SectionRegistry


class Registry(FraguaComponent):
    """Base configuration class for all registry types inside an Environment."""

    def __init__(self, registry_name: str) -> None:
        """Initialize the registry."""
        super().__init__(component_name=registry_name)
        self._sections: Dict[str, SectionRegistry] = {}

    # ---------------------------------------------------------
    # Validation helpers
    # ---------------------------------------------------------

    def _exists(self, key: str) -> bool:
        """Return True if the section exists."""
        return key in self._sections

    def _not_exists(self, key: str) -> bool:
        """Return True if the section does not exist."""
        return key not in self._sections

    # ---------------------------------------------------------
    # CRUD operations for sections
    # ---------------------------------------------------------

    def create_section(self, name: str, section: SectionRegistry) -> bool:
        """Create a new section."""
        if self._not_exists(name):
            self._sections[name] = section
            return True
        return False

    def get_section(self, name: str) -> Optional[SectionRegistry]:
        """Retrieve a section by name."""
        return self._sections.get(name)

    def get_sections(self) -> Dict[str, SectionRegistry]:
        """Retrieve all registered sections."""
        return self._sections

    def update_section(self, old_name: str, new_name: str) -> bool:
        """Rename a section."""
        if self._exists(old_name) and self._not_exists(new_name):
            self._sections[new_name] = self._sections.pop(old_name)
            return True
        return False

    def delete_section(self, name: str) -> bool:
        """Delete a section."""
        return self._sections.pop(name, None) is not None

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------
    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        """Return a structured summary of this Registry."""

    # ---------------------------------------------------------

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"
