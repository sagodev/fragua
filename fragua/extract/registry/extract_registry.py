"""Extract Registry Class."""

from typing import cast
from fragua.core.registry import Registry
from fragua.extract.registry.extract_sets import (
    ExtractAgentSet,
    ExtractFunctionSet,
    ExtractParamsSet,
    ExtractStyleSet,
)


class ExtractRegistry(Registry):
    """
    Extract Registry Class.
    This class registry contains the functions, params, styles
    and agent related to extract action.
    """

    def __init__(self, registry_name: str) -> None:
        super().__init__(registry_name)
        self._initialize_sets()

    def _initialize_sets(self) -> None:
        """Initialize extract sets."""
        extract_fg_sets = {
            "params": ExtractParamsSet(),
            "styles": ExtractStyleSet(),
            "functions": ExtractFunctionSet(),
            "agents": ExtractAgentSet(),
        }

        for name_set, cls_set in extract_fg_sets.items():
            self.create_set(name_set, cls_set)

    @property
    def params(self) -> ExtractParamsSet:
        """Retrive all extract params."""
        return cast(ExtractParamsSet, self.get_sets()["params"])

    @property
    def functions(self) -> ExtractFunctionSet:
        """Retrive all extract functions."""
        return cast(ExtractFunctionSet, self.get_sets()["functions"])

    @property
    def styles(self) -> ExtractStyleSet:
        """Retrive all extract styles."""
        return cast(ExtractStyleSet, self.get_sets()["styles"])

    @property
    def agents(self) -> ExtractAgentSet:
        """Retrive all extract agents."""
        return cast(ExtractAgentSet, self.get_sets()["agents"])

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"
