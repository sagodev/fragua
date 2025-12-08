"""Load Registry Class."""

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

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"
