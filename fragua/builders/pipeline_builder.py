"""Pipeline Builder class."""

from typing import Iterable, List

from fragua.builders.step_builder import FraguaStepBuilder
from fragua.core.pipeline import FraguaPipeline
from fragua.core.step import FraguaStep


class FraguaPipelineBuilder:
    """
    Mutable builder for FraguaPipeline.

    Responsible for assembling and validating
    an ordered sequence of FraguaStep objects.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._steps: List[FraguaStep] = []

    @classmethod
    def from_dict(cls, data: dict) -> "FraguaPipelineBuilder":
        """Create an pipeline builder from an declarative dict."""
        try:
            name = data["name"]
            steps = data["steps"]
        except KeyError as exc:
            raise ValueError(f"Missing pipeline field: {exc}") from exc

        if not isinstance(steps, list):
            raise TypeError("'steps' must be a list")

        builder = cls(name=name)

        for step_def in steps:
            step = FraguaStepBuilder.from_dict(step_def).build()
            builder.add(step)

        return builder

    def add(self, *steps: FraguaStep) -> "FraguaPipelineBuilder":
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

    def extend(self, steps: Iterable[FraguaStep]) -> "FraguaPipelineBuilder":
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

            key = step.save_as or step.function
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

        pipeline = FraguaPipeline(self.name)
        pipeline.add(list(self._steps))
        return pipeline
