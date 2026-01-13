"""Fragua execution box.

Represents the final output of a pipeline execution.
"""

from typing import Any, Dict

# pylint: disable=too-few-public-methods


class FraguaBox:
    """Represents the final output of a pipeline execution."""

    def __init__(
        self,
        *,
        key: str,
        result: dict[str, object],
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        """Initialize a FraguaBox instance.

        Args:
            key: Unique identifier for the execution box
            result: Dictionary containing execution results
            metadata: Optional metadata about the execution
        """
        self.key = key
        self.result = result
        self.metadata = metadata or {}

    def summary(self) -> dict[str, Any]:
        """Return a summary of the execution box.

        Returns:
            Dictionary containing key information about the execution
            including outputs, status, and duration.
        """
        return {
            "key": self.key,
            "outputs": list(self.result.keys()),
            "status": self.metadata.get("execution", {}).get("status"),
            "duration_ms": self.metadata.get("execution", {}).get("duration_ms"),
        }

    def describe(self) -> str:
        """Generate a detailed description of the execution box.

        Returns:
            Formatted string containing information about the agent,
            pipeline, steps executed, and their details.
        """
        lines: list[str] = []

        lines.append(f"FraguaBox: {self.key}")

        agent = self.metadata.get("agent", {})
        lines.append(f"- Agent: {agent.get('name', 'unknown')}")

        pipeline = self.metadata.get("pipeline", {})
        lines.append(f"- Pipeline: {pipeline.get('name', 'unknown')}")
        lines.append(f"- Final step: {pipeline.get('final_step', 'unknown')}")

        steps_meta = self.metadata.get("steps", {})
        total_steps = steps_meta.get("total", "n/a")
        lines.append(f"- Steps executed: {total_steps}")

        step_items = steps_meta.get("items", [])
        if step_items:
            lines.append("- Step details:")
            for step in step_items:
                lines.append(
                    f"  • {step.get('function', 'unknown')} "
                    f"(set={step.get('set')}, status={step.get('status', 'ok')})"
                )

        return "\n".join(lines)

    def get_output(self, key: str) -> object:
        """Retrieve a specific output from the execution result.

        Args:
            key: The key of the output to retrieve

        Returns:
            The output value associated with the given key

        Raises:
            KeyError: If the output key is not found in the result
        """
        if key not in self.result:
            raise KeyError(f"Output '{key}' not found in FraguaBox.")
        return self.result[key]

    def has_errors(self) -> bool:
        """Check if the execution contains any errors.

        Returns:
            True if errors are present in metadata, False otherwise
        """
        return bool(self.metadata.get("errors"))

    def to_dict(self) -> dict[str, Any]:
        """Convert the execution box to a dictionary representation.

        Returns:
            Dictionary containing the key, result, and metadata
        """
        return {
            "key": self.key,
            "result": self.result,
            "metadata": self.metadata,
        }
