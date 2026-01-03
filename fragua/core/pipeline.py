"""Pipeline class."""

from fragua.core.step import FraguaStep


class FraguaPipeline:
    """
    Ordered collection of execution steps.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._steps: list[FraguaStep] = []

    def add(self, step: FraguaStep) -> None:
        """Add step to pipeline."""
        self._steps.append(step)

    def steps(self) -> list[FraguaStep]:
        """Retrive steps list."""
        return list(self._steps)
