"""
Blacksmith agent responsible for transforming data.

The Blacksmith uses ForgeStyles to process data from Wagons and stores results in Boxes via StorageManager.
"""

from typing import Type, Any
from fragua.agents.transformation.forge_style import ForgeStyle, FORGESTYLE_REGISTRY
from fragua.agents.store.box import Box
from fragua.core.base_agent import BaseAgent


class Blacksmith(BaseAgent[ForgeStyle[Any, Any], Box]):
    style_registry: dict[str, Type[ForgeStyle[Any, Any]]] = FORGESTYLE_REGISTRY
    result_type: Type[Box] = Box
    metadata_table_name: str = "transformations"

    def work(self, *args: Any, **kwargs: Any) -> Box:
        return self.apply_style(*args, **kwargs)
