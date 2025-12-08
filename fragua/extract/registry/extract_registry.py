"""Extract Registry Class."""

from fragua.core.registry import Registry
from fragua.extract.registry.extract_section import (
    ExtractAgentSection,
    ExtractFunctionSection,
    ExtractParamsSection,
    ExtractStyleSection,
)


class ExtractRegistry(Registry):
    """
    Extract Registry Class.
    This class registry contains the functions, params, styles
    and agent related to extract action.
    """

    def __init__(self, registry_name: str) -> None:
        super().__init__(registry_name)
        self._initialize_sections()

    def _initialize_sections(self) -> None:
        """Initialize extract sections."""
        extract_fg_sections = {
            "params": ExtractParamsSection(),
            "styles": ExtractStyleSection(),
            "functions": ExtractFunctionSection(),
            "agents": ExtractAgentSection(),
        }

        for name_section, cls_section in extract_fg_sections.items():
            self.create_section(name_section, cls_section)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"
