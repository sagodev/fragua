"""
Blacksmith agent responsible for transforming data.

The Blacksmith uses ForgeStyles to process data from Wagons
and stores results in Boxes via StorageManager.
"""

from __future__ import annotations

from typing import Type, Any
from fragua.styles.forge_style import ForgeStyle, FORGESTYLE_REGISTRY
from fragua.store.box import Box
from fragua.core.base_agent import BaseAgent


class Blacksmith(BaseAgent[ForgeStyle[Any, Any], Box[Any]]):
    """Agent that applies forge styles to data for transformation."""

    style_registry: dict[str, Type[ForgeStyle[Any, Any]]] = FORGESTYLE_REGISTRY
    result_type: Type[Box[Any]] = Box[Any]
    metadata_table_name: str = "transformations"

    def work(self, *args: Any, **kwargs: Any) -> Box[Any]:
        return self.apply_style(*args, **kwargs)
