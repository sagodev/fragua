"""
Blacksmith agent responsible for transforming data.

The Blacksmith uses ForgeStyles to process data from Wagons and stores results in Boxes via StorageManager.
"""

from typing import Any, Dict
from datetime import datetime, timezone
import pandas as pd
from core.base_agent import BaseAgent
from agents.transformation.forge_style import ForgeStyle, FORGESTYLE_REGISTRY
from agents.store.box import Box
from utils.logger import get_logger

logger = get_logger("Blacksmith")


class Blacksmith(BaseAgent):
    """
    Optimized Blacksmith agent capable of learning and applying ForgeStyles,
    while keeping efficient metadata of its knowledge and transformations.
    """

    def __init__(self, name: str):
        super().__init__(name)
        # Dictionary of learned styles: style_name -> ForgeStyle instance
        self.known_styles: Dict[str, ForgeStyle] = {}

        # Internal metadata
        self.metadata: Dict[str, Any] = {
            "name": name,
            "learned_styles": {},  # style_name -> class + timestamp
            "transformations": pd.DataFrame(
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
    def learn_style(self, forge_style: ForgeStyle):
        """
        Teach the Blacksmith a ForgeStyle.
        Stores it in known_styles and logs metadata.
        """
        self.known_styles[forge_style.style_name] = forge_style
        self.metadata["learned_styles"][forge_style.style_name] = {
            "class": forge_style.__class__.__name__,
            "learned_at": datetime.now(timezone.utc),
        }
        logger.info("Learned style '%s'", forge_style.style_name)

    def learn_style_by_name(self, name: str, **kwargs):
        """
        Teach a ForgeStyle dynamically from the registry.
        """
        if name not in FORGESTYLE_REGISTRY:
            logger.error("No ForgeStyle registered under name '%s'", name)
            raise ValueError(f"No ForgeStyle registered under name '{name}'")
        style_cls = FORGESTYLE_REGISTRY[name]
        style_name = kwargs.pop("style_name", name)
        instance = style_cls(style_name=style_name, **kwargs)
        self.learn_style(instance)

    # ---------------- Working ---------------- #
    def work(self, style_name: str, data: Any) -> Box:
        """
        Apply a learned ForgeStyle to the given data.
        Returns a Box with transformed data and records metadata efficiently.
        """
        if style_name not in self.known_styles:
            logger.error("Style '%s' not learned", style_name)
            raise ValueError(f"Style '{style_name}' not learned")

        forge_style = self.known_styles[style_name]
        result = forge_style.use(data)

        if not isinstance(result, Box):
            logger.error(
                "ForgeStyle '%s' must return a Box, got %s",
                style_name,
                type(result).__name__,
            )
            raise TypeError(
                f"ForgeStyle '{style_name}' must return a Box, got {type(result).__name__}"
            )

        # Record transformation metadata
        new_row = {
            "style_name": style_name,
            "timestamp": datetime.now(timezone.utc),
            "output_name": result.name,
            "rows": getattr(result.data, "shape", [None, None])[0],
            "columns": getattr(result.data, "shape", [None, None])[1],
            "checksum": forge_style.metadata.get("checksum"),
        }
        self.metadata["transformations"] = pd.concat(
            [self.metadata["transformations"], pd.DataFrame([new_row])],
            ignore_index=True,
        )

        logger.info("Applied style '%s'", style_name)
        return result

    # ---------------- Storage Interaction ---------------- #
    def store_result(self, storage_manager, box: Box, wagon_name: str):
        """
        Store the resulting Box in StorageManager.
        """
        storage_manager.save_box(wagon_name, box)
        logger.info("Stored Box '%s' in StorageManager", wagon_name)
