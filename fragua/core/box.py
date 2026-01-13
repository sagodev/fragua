"""Fragua execution box.

Represents the final output of a pipeline execution.
"""

from typing import Any, Dict


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
            key: Unique identifier for the execution box.
            result: Dictionary containing execution results.
            metadata: Normalized execution metadata.
        """
        self.key = key
        self.result = result
        self.metadata = metadata or {}

    # -------------------- High-level views -------------------- #

    def summary(self) -> dict[str, Any]:
        """Return a concise execution summary."""
        execution = self.metadata.get("execution", {})

        return {
            "key": self.key,
            "outputs": list(self.result.keys()),
            "status": execution.get("status"),
            "duration_ms": execution.get("duration_ms"),
            "environment": execution.get("environment"),
        }

    def describe(self) -> str:
        """Generate a detailed human-readable description."""
        lines: list[str] = []

        lines.append(f"FraguaBox: {self.key}")

        agent = self.metadata.get("agent", {})
        lines.append(f"- Agent: {agent.get('name', 'unknown')}")

        pipeline = self.metadata.get("pipeline", {})
        lines.append(f"- Pipeline: {pipeline.get('name', 'unknown')}")
        lines.append(f"- Final step: {pipeline.get('final_step', 'unknown')}")

        steps_meta = self.metadata.get("steps", {})
        total_steps = steps_meta.get("total", 0)
        lines.append(f"- Steps executed: {total_steps}")

        step_items = steps_meta.get("items", [])
        if step_items:
            lines.append("- Step details:")
            for step in step_items:
                origin = step.get("origin")

                origin_info = ""
                if origin and origin.get("type") == "macro":
                    origin_info = (
                        f" [macro:{origin.get('name')} "
                        f"{origin.get('index')}/{origin.get('total')}]"
                    )

                lines.append(
                    f"  • {step.get('function', 'unknown')}"
                    f"{origin_info} "
                    f"(set={step.get('set')}, status={step.get('status', 'ok')})"
                )

        if self.has_errors():
            lines.append("- Errors:")
            for error in self.metadata.get("errors", []):
                lines.append(f"  • {error.get('message')}")

        return "\n".join(lines)

    # -------------------- Access helpers -------------------- #

    def get_output(self, key: str) -> object:
        """Retrieve a specific output value."""
        if key not in self.result:
            raise KeyError(f"Output '{key}' not found in FraguaBox.")
        return self.result[key]

    def has_errors(self) -> bool:
        """Return True if execution errors are present."""
        return bool(self.metadata.get("errors"))

    # -------------------- Serialization -------------------- #

    def to_dict(self) -> dict[str, Any]:
        """Convert the FraguaBox to a dictionary."""
        return {
            "key": self.key,
            "result": self.result,
            "metadata": self.metadata,
        }
