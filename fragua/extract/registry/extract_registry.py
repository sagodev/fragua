"""Extract Registry Class."""

from typing import cast
from fragua.core.registry import Registry
from fragua.extract.registry.extract_sections import (
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

    @property
    def params(self) -> ExtractParamsSection:
        """Retrive all extract params."""
        return cast(ExtractParamsSection, self.get_sections()["params"])

    @property
    def functions(self) -> ExtractFunctionSection:
        """Retrive all extract functions."""
        return cast(ExtractFunctionSection, self.get_sections()["functions"])

    @property
    def styles(self) -> ExtractStyleSection:
        """Retrive all extract styles."""
        return cast(ExtractStyleSection, self.get_sections()["styles"])

    @property
    def agents(self) -> ExtractAgentSection:
        """Retrive all extract agents."""
        return cast(ExtractAgentSection, self.get_sections()["agents"])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"
