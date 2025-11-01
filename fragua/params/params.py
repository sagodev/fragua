"""
Base abstract class for all parameter schemas used by styles in Fragua.
"""

from typing import Dict, Tuple, Type, Any
from pydantic import BaseModel


class Params(BaseModel):
    """Base configuration model shared by all params."""

    class Config:
        """Configuration for the Params model."""

        arbitrary_types_allowed = True  # Allows DataFrame
        extra = "forbid"  # Forbid unexpected fields (strict)


PARAMS_REGISTRY: Dict[Tuple[str, str], Type[Params]] = {}


def register_params(role: str, style: str) -> Any:
    """
    Decorator to register a Params class for a given agent and style.

    Example:
        @register_params(agent="miner", style="excel")
        class ExcelMineParams(MineParams):
            ...
    """

    def decorator(cls: Type[Params]) -> Any:
        PARAMS_REGISTRY[(role, style)] = cls
        return cls

    return decorator


def get_params(role: str, style: str) -> Type[Params]:
    """
    Retrieve the registered Params class for a given role and style.

    Args:
        role (str): Name of the agent role (e.g., "miner", "blacksmith").
        style (str): Name of the style (e.g., "excel", "forge").

    Returns:
        Type[Params]: The registered Params subclass.

    Raises:
        KeyError: If no Params class is registered for the given (role, style).
    """
    try:
        return PARAMS_REGISTRY[(role, style)]
    except KeyError as exc:
        raise KeyError(
            f"No Params class registered for role='{role}', style='{style}'."
        ) from exc
