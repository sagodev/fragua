"""
Global registry for all style classes used by Fragua agents.
"""

from typing import Dict, Tuple, Type, Optional, Any

from fragua.core.base_params import BaseParams
from fragua.core.base_style import BaseStyle
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


# (action, style) -> StyleClass
STYLE_REGISTRY: Dict[Tuple[str, str], Type[BaseStyle[BaseParams, object]]] = {}


def register_style(action: str, style: str) -> Any:
    """
    Decorator to register a Style class for a given (action, style).

    Example:
        @register_style(action="forge", style="ml")
        class MLForgeStyle(ForgeStyle):
            ...
    """

    def decorator(
        cls: Type[BaseStyle[BaseParams, object]],
    ) -> Any:
        key = (action, style)
        if key in STYLE_REGISTRY:
            logger.warning("Overwriting existing style registration for %s", key)
        STYLE_REGISTRY[key] = cls
        logger.debug("Registered style: %s -> %s", key, cls.__name__)
        return cls

    return decorator


def get_style(action: str, style: str) -> Type[BaseStyle[BaseParams, object]]:
    """Retrieve a registered Style class by (action, style)."""
    key = (action, style)
    try:
        return STYLE_REGISTRY[key]
    except KeyError:
        logger.error("Style not found for action='%s', style='%s'", action, style)
        raise KeyError(f"Style not found for action='{action}', style='{style}'")


def list_styles(
    action: Optional[str] = None,
) -> Dict[Tuple[str, str], Type[BaseStyle[BaseParams, object]]]:
    """List all registered styles, optionally filtered by action."""
    if action is not None:
        return {k: v for k, v in STYLE_REGISTRY.items() if k[0] == action}
    return dict(STYLE_REGISTRY)
