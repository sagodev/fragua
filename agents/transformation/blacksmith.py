"""
Blacksmith agent responsible for transforming data.

The Blacksmith uses ForgeStyles to process data from Wagons and stores results in Boxes via StorageManager.
"""

from agents.transformation.forge_style import ForgeStyle, FORGESTYLE_REGISTRY
from agents.store.box import Box
from core.base_agent import BaseAgent


class Blacksmith(BaseAgent):
    style_registry = FORGESTYLE_REGISTRY
    result_type = Box
    metadata_table_name = "transformations"

    def work(self, style_name: str, data):
        return self.apply_style(style_name, data)
