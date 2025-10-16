"""
Miner agent responsible for extracting data using ExtractionStyles.

The Miner now uses ExtractionStyles to process data from sources
and stores results in Wagons via StorageManager.
"""

from agents.extraction.extraction_style import ExtractionStyle, EXTRACTIONSTYLE_REGISTRY
from agents.store.wagon import Wagon
from core.base_agent import BaseAgent


class Miner(BaseAgent):
    style_registry = EXTRACTIONSTYLE_REGISTRY
    result_type = Wagon
    metadata_table_name = "extractions"

    def work(self, style_name: str, source):
        return self.apply_style(style_name, source)
