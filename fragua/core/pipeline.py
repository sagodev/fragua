"""Fragua Pipeline Class."""

from __future__ import annotations
from typing import List, Union
from fragua.core.step import FraguaStep


class FraguaPipeline:
    """
    Ordered collection of execution steps.
    """

    name: str
    _steps: List[FraguaStep]

    def __init__(self, name: str) -> None:
        self.name = name
        self._steps = []

    def validate(self) -> None:
        """Validate step dependencies and uniqueness of outputs."""
        known_keys: set[str] = set()

        for step in self._steps:
            if step.use and step.use not in known_keys:
                raise ValueError(
                    f"Step '{step.function}' depends on unknown step '{step.use}'"
                )

            key: str = step.save_as or step.function
            if key in known_keys:
                raise ValueError(f"Duplicated step output key: {key}")

            known_keys.add(key)

    def add(self, step_or_steps: Union[FraguaStep, List[FraguaStep]]) -> None:
        """
        Add a single step or a list of steps to the pipeline.

        Replaces the current steps if a list is provided.
        """
        if isinstance(step_or_steps, list):
            self._steps = step_or_steps
        elif isinstance(step_or_steps, FraguaStep):
            self._steps.append(step_or_steps)
        else:
            raise TypeError(
                f"{step_or_steps} must be a FraguaStep or a list of FraguaSteps."
            )

    def steps(self) -> List[FraguaStep]:
        """Return a copy of the steps list."""
        return list(self._steps)
