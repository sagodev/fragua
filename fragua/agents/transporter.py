"""
Transporter Class.
"""

from __future__ import annotations

from typing import Type, Any
from fragua.styles.delivery_style import DeliveryStyle, DELIVERYSTYLE_REGISTRY
from fragua.store.container import Container
from fragua.core.base_agent import BaseAgent


class Transporter(BaseAgent[DeliveryStyle[Any, Any], Container[Any]]):
    """Agent that applies delivery styles to data for final delivery."""

    style_registry: dict[str, Type[DeliveryStyle[Any, Any]]] = DELIVERYSTYLE_REGISTRY
    result_type: Type[Container[Any]] = Container

    def work(self, *args: Any, **kwargs: Any) -> Container[Any]:
        """Apply a delivery style to provided data and return a Container result."""
        return self.apply_style(*args, **kwargs)
