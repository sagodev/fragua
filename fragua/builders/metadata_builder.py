"""Metadta builder class."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
import os
import re

from fragua.core.step import FraguaStep

# pylint: disable=too-many-arguments


def _sanitize_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize parameters to remove sensitive information like file paths.

    Args:
        params: Original parameters dictionary

    Returns:
        Sanitized parameters with sensitive information filtered out
    """
    if not params:
        return {}

    sanitized = {}

    for key, value in params.items():
        # Check for potential file paths
        if isinstance(value, str):
            # Detect common file path patterns
            if _is_file_path(value):
                # Extract just the filename without the full path
                sanitized[key] = f"[FILE] {os.path.basename(value)}"
            else:
                sanitized[key] = value
        elif isinstance(value, dict):
            # Recursively sanitize nested dictionaries
            sanitized[key] = _sanitize_params(value)
        elif isinstance(value, list):
            # Handle lists by sanitizing each item if it's a dict or string
            sanitized[key] = [
                (
                    _sanitize_params(item)
                    if isinstance(item, dict)
                    else (
                        f"[FILE] {os.path.basename(item)}"
                        if isinstance(item, str) and _is_file_path(item)
                        else item
                    )
                )
                for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def _is_file_path(text: str) -> bool:
    """
    Check if a string looks like a file path.

    Args:
        text: String to check

    Returns:
        True if the string appears to be a file path
    """
    if not isinstance(text, str):
        return False

    # Check for absolute path patterns
    if re.match(r"^[A-Za-z]:\\\\", text):  # Windows path like C:\\
        return True

    if re.match(r"^[A-Za-z]:/", text):  # Unix-like absolute path like /home/user/
        return True

    # Check for common file extensions
    if re.search(r"\.(xlsx|xls|csv|json|txt|log|py|md)$", text, re.IGNORECASE):
        # Additional check: contains directory separators
        if "\\" in text or "/" in text:
            return True

    return False


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
                "params": _sanitize_params(step.params),
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
