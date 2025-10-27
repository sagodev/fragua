"""
Transporter Class.
"""

from __future__ import annotations

from typing import Type, Any
from fragua.styles.delivery_styles import DeliveryStyle
from fragua.store.container import Container
from fragua.core.base_agent import BaseAgent


class Transporter(BaseAgent[DeliveryStyle[Any, Any], Container[Any]]):
    """Agent that applies delivery styles to data for final delivery."""

    storage_type: Type[Container[Any]] = Container
