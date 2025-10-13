"""Blacksmith: applies transformations to Bagons."""

from time import time
from typing import List
from storage.bagons import Bagon
from blacksmiths.styles.base_style import ForgeStyle
from core.logger import get_logger
from core.metrics import MetricsRegistry

logger = get_logger(__name__)


class Blacksmith:
    """
    Receives Bagons and applies transformations using a ForgeStyle.
    """

    def __init__(
        self,
        style: ForgeStyle,
        name: str = "blacksmith",
        metrics: MetricsRegistry = None,
    ):
        self.style = style
        self.name = name
        self.logger = get_logger(f"fragua.blacksmith.{self.name}")
        self.metrics = metrics or MetricsRegistry()

    def forge(self, bagons: List[Bagon]) -> List[Bagon]:
        """
        Apply the transformation style to each Bagón.
        """
        forged_bagons = []
        for bagon in bagons:
            start = time()
            self.logger.info("Forging Bagón: %s", bagon.name)
            try:
                transformed = self.style.transform(bagon)
                duration = time() - start
                self.metrics.record_event(
                    agent=f"blacksmith.{self.name}",
                    action="transform",
                    bagon_name=bagon.name,
                    rows=len(transformed.data),
                    duration_sec=duration,
                    style=self.style.__class__.__name__,
                )
                self.logger.info(
                    "Bagón %s forged successfully (%s rows in %.2f sec)",
                    bagon.name,
                    len(transformed.data),
                    duration,
                )
                forged_bagons.append(transformed)
            except Exception as e:
                self.logger.exception("Forging failed for Bagón %s: %s", bagon.name, e)
        return forged_bagons
