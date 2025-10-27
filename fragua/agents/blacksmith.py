"""
Blacksmith agent responsible for transforming data.

The Blacksmith uses ForgeStyles to process data from Wagons
and stores results in Boxes via StoreManager.
"""

from __future__ import annotations

from typing import Type, Any
from fragua.styles.forge_styles import ForgeStyle
from fragua.store.box import Box
from fragua.core.base_agent import BaseAgent


class Blacksmith(BaseAgent[ForgeStyle[Any, Any], Box[Any]]):
    """Agent that applies forge styles to data for transformation."""

    storage_type: Type[Box[Any]] = Box[Any]
