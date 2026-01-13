"""Step Class."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Dict


@dataclass(frozen=True)
class FraguaStep:
    """
    Represents a single execution step in a pipeline.
    """

    set_name: str
    function: str
    params: dict[str, Any]
    save_as: Optional[str] = None
    use: Optional[str] = None
    origin: Optional[Dict[str, Any]] = None
