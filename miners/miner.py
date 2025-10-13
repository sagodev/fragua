"""Miner: orchestrates extraction using pickaxes."""

from typing import Iterable, List
from ..miners.pickaxes.base_pickaxe import Pickaxe
from ..storage.bagons import Bagon
from ..core.logger import get_logger

logger = get_logger(__name__)


class Miner:
    """
    Coordinator for extraction. Receives a list of Pickaxe instances and runs them,
    collecting results in Bagons.
    """

    def __init__(self, name: str = "miner"):
        self.name = name
        self.logger = get_logger(f"fragua.miner.{self.name}")

    def extract(self, pickaxes: Iterable[Pickaxe]) -> List[Bagon]:
        """
        Execute each pickaxe's extract() method and return a list of Bagons.
        """
        bagons = []
        for pickaxe in pickaxes:
            self.logger.info("Starting extraction with pickaxe: %s", pickaxe.name)
            try:
                bagon = pickaxe.extract()
                if not isinstance(bagon, Bagon):
                    # If pickaxe returns raw DataFrame, wrap it
                    from ..storage.bagons import Bagon as _Bagon

                    bagon = _Bagon(name=getattr(pickaxe, "name", "unknown"), data=bagon)
                self.logger.info(
                    "Extraction completed: %s rows", bagon.metadata.get("rows")
                )
                bagons.append(bagon)
            except Exception as e:
                self.logger.exception(
                    "Extraction failed for pickaxe %s: %s", pickaxe, e
                )
                raise
        return bagons
