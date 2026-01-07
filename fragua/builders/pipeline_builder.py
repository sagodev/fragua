"""Fragua Pipeline Builder Class."""

from __future__ import annotations
from typing import Iterable, List, Dict

from fragua.builders.step_builder import FraguaStepBuilder
from fragua.core.pipeline import FraguaPipeline
from fragua.core.step import FraguaStep


class FraguaPipelineBuilder:
    """
    Mutable builder for FraguaPipeline.

    Responsible for assembling and validating
    an ordered sequence of FraguaStep objects.
    """

    name: str
    _steps: List[FraguaStep]

    def __init__(self, name: str) -> None:
        self.name = name
        self._steps = []

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> FraguaPipelineBuilder:
        """Create a pipeline builder from a declarative dict."""
        try:
            name: str = data["name"]  # type: ignore
            steps: list = data["steps"]  # type: ignore
        except KeyError as exc:
            raise ValueError(f"Missing pipeline field: {exc}") from exc

        if not isinstance(steps, list):
            raise TypeError("'steps' must be a list")

        builder = cls(name=name)

        for step_def in steps:
            step: FraguaStep = FraguaStepBuilder.from_dict(step_def).build()
            builder.add(step)

        return builder

    def add(self, *steps: FraguaStep) -> FraguaPipelineBuilder:
        """
        Add one or more steps to the pipeline.
        """
        if not steps:
            raise ValueError("At least one FraguaStep must be provided")

        for step in steps:
            if not isinstance(step, FraguaStep):
                raise TypeError("Expected FraguaStep instances")
            self._steps.append(step)

        return self

    def extend(self, steps: Iterable[FraguaStep]) -> FraguaPipelineBuilder:
        """Add multiple steps to the pipeline."""
        for step in steps:
            self.add(step)
        return self

    def validate(self) -> None:
        """Validate pipeline step dependencies and outputs."""
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

        if not self._steps:
            raise ValueError("Pipeline contains no steps")

    def build(self) -> FraguaPipeline:
        """
        Validate and build an immutable FraguaPipeline.
        """
        self.validate()

        pipeline: FraguaPipeline = FraguaPipeline(self.name)
        pipeline.add(list(self._steps))
        return pipeline
