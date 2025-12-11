"""Extract Registry Class."""

from typing import Any, Dict, cast
from fragua.core.registry import FraguaRegistry
from fragua.extract.registry.extract_sets import (
    ExtractAgentSet,
    ExtractFunctionSet,
    ExtractParamsSet,
    ExtractStyleSet,
)


class ExtractRegistry(FraguaRegistry):
    """
    Extract Registry Class.
    This class registry contains the functions, params, styles
    and agent related to extract action.
    """

    def __init__(self, registry_name: str, fg_config: bool) -> None:
        super().__init__(registry_name)
        self._initialize_sets(fg_config)

    def _initialize_sets(self, fg_config: bool) -> None:
        """Initialize extract sets."""
        extract_fg_sets = {
            "params": ExtractParamsSet(fg_config),
            "styles": ExtractStyleSet(fg_config),
            "functions": ExtractFunctionSet(fg_config),
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

    def summary(self) -> Dict[str, Any]:
        """
        Extract registry summary.
        """

        return {
            "params": self.params.summary(),
            "functions": self.functions.summary(),
            "styles": self.styles.summary(),
            "agents": self.agents.summary(),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"
