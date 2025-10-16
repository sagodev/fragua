"""
Transporter Class.
"""

from agents.loading.delivery_style import DeliveryStyle, DELIVERYSTYLE_REGISTRY
from agents.store.container import Container
from core.base_agent import BaseAgent


class Transporter(BaseAgent):
    style_registry = DELIVERYSTYLE_REGISTRY
    result_type = Container
    metadata_table_name = "Deliveries"
