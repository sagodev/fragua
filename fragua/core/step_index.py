"""Step index class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fragua.builders.step_builder import FraguaStepBuilder

if TYPE_CHECKING:
    from typing import List


class FraguaStepIndex:
    """
    Index of FraguaStepBuilder templates.

    Provides discoverable, safe access to preconfigured
    step builders associated with registered functions.
    """

    def __init__(self) -> None:
        self._steps: dict[str, FraguaStepBuilder] = {}

    def register(
        self,
        *,
        name: str,
        builder: FraguaStepBuilder,
    ) -> None:
        """Register FraguaStepBuilder object."""
        if name in self._steps:
            raise ValueError(f"Step already registered: {name}")

        self._steps[name] = builder

    def get(self, name: str) -> FraguaStepBuilder:
        """Retrive FraguaStepBuilder object from index."""
        if name not in self._steps:
            raise KeyError(f"Step not found: {name}")

        template = self._steps[name]
        return FraguaStepBuilder(
            set_name=template.set_name,
            function=template.function,
        )

    def list(self) -> List[str]:
        """Return the list of registered item names."""
        return sorted(self._steps.keys())
