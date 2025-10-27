"""
Global registry for all style classes used by Fragua agents.
"""

from typing import Dict, Tuple, Type, Any
from fragua.core.base_style import BaseStyle
from fragua.utils.logger import get_logger


logger = get_logger(__name__)

# (action, style) -> StyleClass
STYLE_REGISTRY: Dict[Tuple[str, str], Type[BaseStyle[Any, Any]]] = {}


def register_style(action: str, style: str) -> Any:
    """
    Decorator to register a Style class for a given action and style.

    Example:
        @register_style(action="forge", style="ml")
        class MLForgeStyle(ForgeStyle):
            ...
    """

    def decorator(cls: Type[BaseStyle[Any, Any]]) -> Any:
        key = (action, style)
        if key in STYLE_REGISTRY:
            logger.warning("Overwriting existing style registration for %s", key)
        STYLE_REGISTRY[key] = cls
        logger.debug("Registered style: %s -> %s", key, cls.__name__)
        return cls

    return decorator


def get_style(action: str, style: str) -> Type[BaseStyle[Any, Any]]:
    """Retrieve a registered Style class by (action, style)."""
    key = (action, style)
    if key not in STYLE_REGISTRY:
        raise KeyError(f"Style not found for action='{action}', style='{style}'")
    return STYLE_REGISTRY[key]


def list_styles(
    action: str | None = None,
) -> Dict[Tuple[str, str], Type[BaseStyle[Any, Any]]]:
    """List all registered styles, optionally filtered by action."""
    if action:
        return {k: v for k, v in STYLE_REGISTRY.items() if k[0] == action}
    return dict(STYLE_REGISTRY)
