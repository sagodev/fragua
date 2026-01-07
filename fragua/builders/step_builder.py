from __future__ import annotations
from typing import Any, Dict, Optional

from fragua.core.step import FraguaStep


class FraguaStepBuilder:
    """
    Mutable builder for FraguaStep.
    """

    set_name: str
    function: str
    params: Dict[str, Any]
    save_as: Optional[str]
    use: Optional[str]

    def __init__(self, *, set_name: str, function: str) -> None:
        self.set_name = set_name
        self.function = function
        self.params = {}
        self.save_as = None
        self.use = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FraguaStepBuilder:
        """Create a step builder from a declarative dict."""
        try:
            builder = cls(
                set_name=data["set"],
                function=data["function"],
            )
        except KeyError as exc:
            raise ValueError(f"Missing required step field: {exc}") from exc

        if "params" in data and isinstance(data["params"], dict):
            builder.with_params(**data["params"])

        if "use" in data and isinstance(data["use"], str):
            builder.with_use(data["use"])

        if "save_as" in data and isinstance(data["save_as"], str):
            builder.with_save_as(data["save_as"])

        return builder

    def with_params(self, **params: Any) -> FraguaStepBuilder:
        """Set step params."""
        self.params.update(params)
        return self

    def with_save_as(self, name: str) -> FraguaStepBuilder:
        """Set 'save_as' step argument."""
        self.save_as = name
        return self

    def with_use(self, name: str) -> FraguaStepBuilder:
        """Set 'use' step argument."""
        self.use = name
        return self

    def copy(self) -> FraguaStepBuilder:
        """Return a StepBuilder copy."""
        builder_copy = FraguaStepBuilder(
            set_name=self.set_name,
            function=self.function,
        )
        builder_copy.params = dict(self.params)
        builder_copy.save_as = self.save_as
        builder_copy.use = self.use
        return builder_copy

    def build(self) -> FraguaStep:
        """Finalize and return an immutable FraguaStep."""
        return FraguaStep(
            set_name=self.set_name,
            function=self.function,
            params=dict(self.params),  # defensive copy
            save_as=self.save_as,
            use=self.use,
        )
