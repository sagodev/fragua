"""Forge: orchestrates multiple Blacksmiths."""

from typing import List
from storage.bagons import Bagon
from blacksmiths.blacksmith import Blacksmith
from core.logger import get_logger

logger = get_logger(__name__)


class Forge:
    """
    Orchestrator that applies a sequence of Blacksmiths to Bagons.
    """

    def __init__(self, blacksmiths: List[Blacksmith]):
        self.blacksmiths = blacksmiths
        self.logger = get_logger("fragua.forge")

    def execute(self, bagons: List[Bagon]) -> List[Bagon]:
        """
        Apply all blacksmiths in sequence to the list of Bagons.
        """
        current_bagons = bagons
        for bs in self.blacksmiths:
            self.logger.info("Applying Blacksmith: %s", bs.name)
            current_bagons = bs.forge(current_bagons)
        return current_bagons
