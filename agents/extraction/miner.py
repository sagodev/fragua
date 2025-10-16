"""
Miner agent responsible for extracting data using ExtractionStyles.

The Miner now uses ExtractionStyles to process data from sources
and stores results in Wagons via StorageManager.
"""

from typing import Any, Dict
from datetime import datetime, UTC
import pandas as pd
from core.base_agent import BaseAgent
from agents.extraction.extraction_style import ExtractionStyle, EXTRACTIONSTYLE_REGISTRY
from agents.store.wagon import Wagon
from utils.logger import get_logger

logger = get_logger("Miner")


class Miner(BaseAgent):
    """
    Optimized Miner agent capable of learning and applying ExtractionStyles,
    while keeping efficient metadata of its knowledge and extractions.
    """

    def __init__(self, name: str):
        super().__init__(name)
        # Dictionary of learned styles: style_name -> ExtractionStyle instance
        self.known_styles: Dict[str, ExtractionStyle] = {}

        # Internal metadata
        self.metadata: Dict[str, Any] = {
            "name": name,
            "learned_styles": {},  # style_name -> class + timestamp
            "extractions": pd.DataFrame(
                columns=[
                    "style_name",
                    "timestamp",
                    "output_name",
                    "rows",
                    "columns",
                    "checksum",
                ]
            ),
        }

    # ---------------- Learning ---------------- #
    def learn_style(self, style: ExtractionStyle):
        """
        Teach the Miner an ExtractionStyle.
        Stores it in known_styles and logs metadata.
        """
        self.known_styles[style.style_name] = style
        self.metadata["learned_styles"][style.style_name] = {
            "class": style.__class__.__name__,
            "learned_at": datetime.now(UTC),
        }
        logger.info("Learned style '%s'", style.style_name)

    def learn_style_by_name(self, name: str, **kwargs):
        """
        Teach an ExtractionStyle dynamically from the registry.
        """
        if name not in EXTRACTIONSTYLE_REGISTRY:
            logger.error("No ExtractionStyle registered under name '%s'", name)
            raise ValueError(f"No ExtractionStyle registered under name '{name}'")
        style_cls = EXTRACTIONSTYLE_REGISTRY[name]
        style_name = kwargs.pop("style_name", name)
        instance = style_cls(style_name=style_name, **kwargs)
        self.learn_style(instance)

    # ---------------- Working ---------------- #
    def work(self, style_name: str, source: Any) -> Wagon:
        """
        Apply a learned ExtractionStyle to the given source.
        Returns a Wagon with extracted data and records metadata efficiently.
        """
        if style_name not in self.known_styles:
            logger.error("Style '%s' not learned", style_name)
            raise ValueError(f"Style '{style_name}' not learned")

        style = self.known_styles[style_name]
        result = style.use(source)

        if not isinstance(result, Wagon):
            logger.error(
                "ExtractionStyle '%s' must return a Wagon, got %s",
                style_name,
                type(result).__name__,
            )
            raise TypeError(
                f"ExtractionStyle '{style_name}' must return a Wagon, got {type(result).__name__}"
            )

        # Record extraction metadata
        new_row = {
            "style_name": style_name,
            "timestamp": datetime.now(UTC),
            "output_name": result.name,
            "rows": getattr(result.data, "shape", [None, None])[0],
            "columns": getattr(result.data, "shape", [None, None])[1],
            "checksum": getattr(result, "checksum", None),
        }
        self.metadata["extractions"] = pd.concat(
            [self.metadata["extractions"], pd.DataFrame([new_row])],
            ignore_index=True,
        )

        logger.info("Applied style '%s'", style_name)
        return result

    # ---------------- Storage Interaction ---------------- #
    def store_result(self, storage_manager, wagon: Wagon, wagon_name: str):
        """
        Store the resulting Wagon in StorageManager.
        """
        storage_manager.save_wagon(wagon_name, wagon)
        logger.info("Stored Wagon '%s' in StorageManager", wagon_name)
