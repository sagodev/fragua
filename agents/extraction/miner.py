"""
Miner agent responsible for extracting data using ExtractionStyles.

The Miner now uses ExtractionStyles to process data from sources
and stores results in Wagons via StorageManager.
"""

from typing import Type, Any
from agents.extraction.extraction_style import ExtractionStyle, EXTRACTIONSTYLE_REGISTRY
from agents.store.wagon import Wagon
from core.base_agent import BaseAgent


class Miner(BaseAgent[ExtractionStyle[Any], Wagon]):
    style_registry: dict[str, Type[ExtractionStyle[Any]]] = EXTRACTIONSTYLE_REGISTRY
    result_type: Type[Wagon] = Wagon
    metadata_table_name: str = "extractions"

    def work(self, *args: Any, **kwargs: Any) -> Wagon:
        return self.apply_style(*args, **kwargs)
