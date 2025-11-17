"""Summary utilities for Fragua."""

from __future__ import annotations
from typing import Any
from dataclasses import is_dataclass, asdict


def summary(obj: Any) -> Any:  # pylint: disable=R0911
    """
    Generic summarization utility that converts any object into a JSON-serializable structure.
    """

    # Object implements its own summary()
    if hasattr(obj, "summary") and callable(obj.summary):
        return obj.summary()

    # Pydantic BaseModel
    if hasattr(obj, "model_dump"):
        return obj.model_dump()

    # Dataclass instance only (avoid dataclass classes)
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)

    # Dict
    if isinstance(obj, dict):
        return {k: summary(v) for k, v in obj.items()}

    # List / Tuple
    if isinstance(obj, (list, tuple)):
        return [summary(x) for x in obj]

    # Normal object with attributes
    if hasattr(obj, "__dict__"):
        return {
            "type": type(obj).__name__,
            **{k: summary(v) for k, v in obj.__dict__.items()},
        }

    # Primitive value (str, int, float, None, bool)
    return obj
