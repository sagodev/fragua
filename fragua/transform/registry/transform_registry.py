"""Transform Registry Class."""

from typing import Any, Dict, cast
from fragua.core.registry import FraguaRegistry
from fragua.transform.registry.transform_sets import (
    TransformAgentSet,
    TransformFunctionSet,
    TransformParamsSet,
    TransformStyleSet,
)


class TransformRegistry(FraguaRegistry):
    """
    Transform Registry Class.
    This class registry contains the functions, params, styles
    and agent related to transform action.
    """

    def __init__(self, registry_name: str, fg_config: bool) -> None:
        super().__init__(registry_name)
        self._initialize_sets(fg_config)

    def _initialize_sets(self, fg_config: bool) -> None:
        """Initialize transform sets."""
        transform_fg_sets = {
            "params": TransformParamsSet(fg_config),
            "styles": TransformStyleSet(fg_config),
            "functions": TransformFunctionSet(fg_config),
            "agents": TransformAgentSet(),
        }

        for name_set, cls_set in transform_fg_sets.items():
            self.create_set(name_set, cls_set)

    @property
    def params(self) -> TransformParamsSet:
        """Retrive all transform params."""
        return cast(TransformParamsSet, self.get_sets()["params"])

    @property
    def functions(self) -> TransformFunctionSet:
        """Retrive all transform functions."""
        return cast(TransformFunctionSet, self.get_sets()["functions"])

    @property
    def styles(self) -> TransformStyleSet:
        """Retrive all transform styles."""
        return cast(TransformStyleSet, self.get_sets()["styles"])

    @property
    def agents(self) -> TransformAgentSet:
        """Retrive all transform agents."""
        return cast(TransformAgentSet, self.get_sets()["agents"])

    def summary(self) -> Dict[str, Any]:
        """
        Transform registry summary.
        """

        return {
            "params": self.params.summary(),
            "functions": self.functions.summary(),
            "styles": self.styles.summary(),
            "agents": self.agents.summary(),
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"
