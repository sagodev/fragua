"""Metadta builder class."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fragua.core.step import FraguaStep


class MetadataBuilder:
    """
    Builder responsible for collecting and normalizing
    execution metadata during pipeline execution.
    """

    def __init__(
        self,
        *,
        environment: str,
        agent_name: str,
        pipeline_name: str,
    ) -> None:
        self._environment = environment
        self._agent_name = agent_name
        self._pipeline_name = pipeline_name

        self._started_at = datetime.utcnow()
        self._finished_at: Optional[datetime] = None

        self._steps: List[Dict[str, Any]] = []
        self._errors: List[Dict[str, Any]] = []

    # -------------------- Step registration -------------------- #

    def add_step(
        self,
        *,
        order: int,
        step: FraguaStep,
        produced_key: str,
        status: str = "ok",
        origin: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a single executed step.
        """
        self._steps.append(
            {
                "order": order,
                "set": step.set_name,
                "function": step.function,
                "params": step.params,
                "used_input": step.use,
                "produced_key": produced_key,
                "status": status,
                "origin": origin,
            }
        )

    # -------------------- Error handling -------------------- #

    def add_error(
        self,
        *,
        step_order: Optional[int],
        message: str,
        exc: Optional[Exception] = None,
    ) -> None:
        """
        Register an execution error.
        """
        self._errors.append(
            {
                "step_order": step_order,
                "message": message,
                "exception": repr(exc) if exc else None,
            }
        )

    # -------------------- Finalization -------------------- #

    def finalize(
        self,
        *,
        final_step_key: str,
    ) -> Dict[str, Any]:
        """
        Produce normalized execution metadata.
        """
        self._finished_at = datetime.utcnow()

        duration_ms = int((self._finished_at - self._started_at).total_seconds() * 1000)

        return {
            "agent": {
                "name": self._agent_name,
            },
            "pipeline": {
                "name": self._pipeline_name,
                "final_step": final_step_key,
                "steps_count": len(self._steps),
            },
            "steps": {
                "total": len(self._steps),
                "items": self._steps,
            },
            "execution": {
                "environment": self._environment,
                "status": "failed" if self._errors else "success",
                "started_at": self._started_at.isoformat(),
                "finished_at": self._finished_at.isoformat(),
                "duration_ms": duration_ms,
                "error": self._errors[0] if self._errors else None,
            },
            "errors": self._errors or None,
        }
