"""
Base abstract class for all parameter schemas used by styles in Fragua.
"""

from typing import Dict, Tuple, Type, Any
from pydantic import BaseModel


class BaseParams(BaseModel):
    """Base configuration model shared by all params."""

    class Config:
        """Configuration for the BaseParams model."""

        arbitrary_types_allowed = True  # Allows DataFrame
        extra = "forbid"  # Forbid unexpected fields (strict)


PARAMS_REGISTRY: Dict[Tuple[str, str], Type[BaseParams]] = {}


def register_params(agent: str, style: str) -> Any:
    """
    Decorator to register a Params class for a given agent and style.

    Example:
        @register_params(agent="miner", style="excel")
        class ExcelMineParams(MineParams):
            ...
    """

    def decorator(cls: Type[BaseParams]) -> Any:
        PARAMS_REGISTRY[(agent, style)] = cls
        return cls

    return decorator
