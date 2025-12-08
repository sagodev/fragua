"""Load Registry Class."""

from typing import cast
from fragua.core.registry import Registry
from fragua.load.registry.load_sections import (
    LoadAgentSection,
    LoadFunctionSection,
    LoadParamsSection,
    LoadStyleSection,
)


class LoadRegistry(Registry):
    """
    Load Registry Class.
    This class registry contains the functions, params, styles
    and agent related to load action.
    """

    def __init__(self, registry_name: str) -> None:
        super().__init__(registry_name)
        self._initialize_sections()

    def _initialize_sections(self) -> None:
        """Initialize load sections."""
        load_fg_sections = {
            "params": LoadParamsSection(),
            "styles": LoadStyleSection(),
            "functions": LoadFunctionSection(),
            "agents": LoadAgentSection(),
        }

        for name_section, cls_section in load_fg_sections.items():
            self.create_section(name_section, cls_section)

    @property
    def params(self) -> LoadParamsSection:
        """Retrive all load params."""
        return cast(LoadParamsSection, self.get_sections()["params"])

    @property
    def functions(self) -> LoadFunctionSection:
        """Retrive all load functions."""
        return cast(LoadFunctionSection, self.get_sections()["functions"])

    @property
    def styles(self) -> LoadStyleSection:
        """Retrive all load styles."""
        return cast(LoadStyleSection, self.get_sections()["styles"])

    @property
    def agents(self) -> LoadAgentSection:
        """Retrive all load agents."""
        return cast(LoadAgentSection, self.get_sections()["agents"])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"
