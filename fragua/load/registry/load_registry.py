"""Load Registry Class."""

from typing import Any, Dict, cast
from fragua.core.registry import FraguaRegistry
from fragua.load.registry.load_sets import (
    LoadAgentSet,
    LoadFunctionSet,
    LoadParamsSet,
    LoadStyleSet,
)


class LoadRegistry(FraguaRegistry):
    """
    Load Registry Class.
    This class registry contains the functions, params, styles
    and agent related to load action.
    """

    def __init__(self, registry_name: str, fg_config: bool) -> None:
        super().__init__(registry_name)
        self._initialize_sets(fg_config)

    def _initialize_sets(self, fg_config: bool) -> None:
        """Initialize load sets."""
        load_fg_sets = {
            "params": LoadParamsSet(fg_config),
            "styles": LoadStyleSet(fg_config),
            "functions": LoadFunctionSet(fg_config),
            "agents": LoadAgentSet(),
        }

        for name_set, cls_set in load_fg_sets.items():
            self.create_set(name_set, cls_set)

    @property
    def params(self) -> LoadParamsSet:
        """Retrive all load params."""
        return cast(LoadParamsSet, self.get_sets()["params"])

    @property
    def functions(self) -> LoadFunctionSet:
        """Retrive all load functions."""
        return cast(LoadFunctionSet, self.get_sets()["functions"])

    @property
    def styles(self) -> LoadStyleSet:
        """Retrive all load styles."""
        return cast(LoadStyleSet, self.get_sets()["styles"])

    @property
    def agents(self) -> LoadAgentSet:
        """Retrive all load agents."""
        return cast(LoadAgentSet, self.get_sets()["agents"])

    def summary(self) -> Dict[str, Any]:
        """
        Load registry summary.
        """

        return {
            "params": self.params.summary(),
            "functions": self.functions.summary(),
            "styles": self.styles.summary(),
            "agents": self.agents.summary(),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"
