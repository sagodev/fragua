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
