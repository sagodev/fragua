"""Step Class."""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class FraguaStep:
    """
    Represents a single execution step in a pipeline.
    """

    function: str
    params: Dict[str, Any]
    save_as: Optional[str] = None
    use: Optional[str] = None
