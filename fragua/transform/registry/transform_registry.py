"""Transform Registry Class."""

from fragua.core.registry import Registry
from fragua.transform.registry.transform_sections import (
    TransformAgentSection,
    TransformFunctionSection,
    TransformParamsSection,
    TransformStyleSection,
)


class TransformRegistry(Registry):
    """
    Transform Registry Class.
    This class registry contains the functions, params, styles
    and agent related to transform action.
    """

    def __init__(self, registry_name: str) -> None:
        super().__init__(registry_name)
        self._initialize_sections()

    def _initialize_sections(self) -> None:
        """Initialize transform sections."""
        transform_fg_sections = {
            "params": TransformParamsSection(),
            "styles": TransformStyleSection(),
            "functions": TransformFunctionSection(),
            "agents": TransformAgentSection(),
        }

        for name_section, cls_section in transform_fg_sections.items():
            self.create_section(name_section, cls_section)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"
