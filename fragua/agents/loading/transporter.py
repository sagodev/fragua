"""
Transporter Class.
"""

from typing import Type, Any
from fragua.agents.loading.delivery_style import DeliveryStyle, DELIVERYSTYLE_REGISTRY
from fragua.agents.store.container import Container
from fragua.core.base_agent import BaseAgent


class Transporter(BaseAgent[DeliveryStyle[Any], Container]):
    style_registry: dict[str, Type[DeliveryStyle[Any]]] = DELIVERYSTYLE_REGISTRY
    result_type: Type[Container] = Container
    metadata_table_name: str = "deliveries"

    def work(self, *args: Any, **kwargs: Any) -> Container:
        """Apply a delivery style to provided data and return a Container result."""
        return self.apply_style(*args, **kwargs)
