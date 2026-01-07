"""Step builder class."""

from typing import Any, Dict, Optional

from fragua.core.step import FraguaStep


class FraguaStepBuilder:
    """
    Mutable builder for FraguaStep.
    """

    def __init__(self, *, set_name: str, function: str) -> None:
        self.set_name = set_name
        self.function = function
        self.params: Dict[str, Any] = {}
        self.save_as: Optional[str] = None
        self.use: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "FraguaStepBuilder":
        """Create a step builder from a declarative dict."""
        try:
            builder = cls(
                set_name=data["set"],
                function=data["function"],
            )
        except KeyError as exc:
            raise ValueError(f"Missing required step field: {exc}") from exc

        if "params" in data:
            builder.with_params(**data["params"])

        if "use" in data:
            builder.with_use(data["use"])

        if "save_as" in data:
            builder.with_save_as(data["save_as"])

        return builder

    def with_params(self, **params: Any) -> "FraguaStepBuilder":
        """Set step params."""
        self.params.update(params)
        return self

    def with_save_as(self, name: str) -> "FraguaStepBuilder":
        """Set 'save_as' step argument."""
        self.save_as = name
        return self

    def with_use(self, name: str) -> "FraguaStepBuilder":
        """Set 'use' step argument."""
        self.use = name
        return self

    def copy(self) -> "FraguaStepBuilder":
        """Return an StepBuilder copy."""
        return FraguaStepBuilder(
            set_name=self.set_name,
            function=self.function,
        )

    def build(self) -> FraguaStep:
        """
        Finalize and return an immutable FraguaStep.
        """

        return FraguaStep(
            set_name=self.set_name,
            function=self.function,
            params=dict(self.params),  # defensive copy
            save_as=self.save_as,
            use=self.use,
        )
