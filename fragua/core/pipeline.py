"""Pipeline class."""

from typing import List
from fragua.core.step import FraguaStep


class FraguaPipeline:
    """
    Ordered collection of execution steps.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._steps: List[FraguaStep] = []

    def add(self, step_or_steps: FraguaStep | List[FraguaStep]) -> None:
        """Add an step or an ordened sequence of steps to pipeline."""
        if isinstance(step_or_steps, list):
            self._steps = step_or_steps
            return
        if isinstance(step_or_steps, FraguaStep):
            self._steps.append(step_or_steps)
            return

        raise ValueError(
            f"{step_or_steps} most be a FraguaStep or a order list of FraguaSteps."
        )

    def steps(self) -> List[FraguaStep]:
        """Retrive steps list."""
        return list(self._steps)
