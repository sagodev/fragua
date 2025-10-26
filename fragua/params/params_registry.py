"""
Global registry for parameter classes used by agents and styles.
"""

from typing import Dict, Tuple, Type, Any
from fragua.core.base_params import BaseParams

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
