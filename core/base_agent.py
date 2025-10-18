"""
Base class for all ETL agents in Fragua.

Defines the common interface and shared behavior for
agents like Miner, Blacksmith, and Transporter.
"""

from abc import ABC, abstractmethod
from datetime import datetime, UTC
from typing import Any, Dict, Type
import pandas as pd
from utils.logger import get_logger

logger = get_logger("BaseAgent")


class BaseAgent(ABC):
    """
    Abstract base class for ETL agents with built-in support
    for learning and applying registered styles.
    """

    # Subclasses must override these
    style_registry: Dict[str, Type] = {}
    result_type: Type = object
    metadata_table_name: str = "operations"

    def __init__(self, name: str):
        """
        Initialize the agent with a given name.

        Args:
            name (str): The name of the agent.
        """
        self.name = name
        self.known_styles: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {
            "name": name,
            "learned_styles": {},
            self.metadata_table_name: pd.DataFrame(
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
    def learn_style(self, style_instance: Any):
        """
        Register a style instance and record its metadata.
        """
        self.known_styles[style_instance.style_name] = style_instance
        self.metadata["learned_styles"][style_instance.style_name] = {
            "class": style_instance.__class__.__name__,
            "learned_at": datetime.now(UTC),
        }
        logger.info("[%s] Learned style '%s'", self.name, style_instance.style_name)

    def learn_style_by_name(self, name: str, **kwargs):
        """
        Create and learn a style dynamically from the registry.
        """
        if name not in self.style_registry:
            logger.error("[%s] No style registered under '%s'", self.name, name)
            raise ValueError(f"No style registered under name '{name}'")

        style_cls = self.style_registry[name]
        style_name = kwargs.pop("style_name", name)
        instance = style_cls(style_name=style_name, **kwargs)
        self.learn_style(instance)

    # ---------------- Working ---------------- #
    def apply_style(self, style_name: str, data: Any):
        """
        Apply a learned style and record operation metadata.
        """
        if style_name not in self.known_styles:
            logger.error("[%s] Style '%s' not learned", self.name, style_name)
            raise ValueError(f"Style '{style_name}' not learned")

        style = self.known_styles[style_name]
        result = style.use(data)

        if not isinstance(result, self.result_type):
            logger.error(
                "[%s] Style '%s' must return %s, got %s",
                self.name,
                style_name,
                self.result_type.__name__,
                type(result).__name__,
            )
            raise TypeError(
                f"Style '{style_name}' must return {self.result_type.__name__}, got {type(result).__name__}"
            )

        new_row = {
            "style_name": style_name,
            "timestamp": datetime.now(UTC),
            "output_name": getattr(result, "name", None),
            "rows": getattr(getattr(result, "data", None), "shape", [None, None])[0],
            "columns": getattr(getattr(result, "data", None), "shape", [None, None])[1],
            "checksum": getattr(getattr(style, "metadata", {}), "get", lambda _: None)(
                "checksum"
            ),
        }
        self.metadata[self.metadata_table_name] = pd.concat(
            [self.metadata[self.metadata_table_name], pd.DataFrame([new_row])],
            ignore_index=True,
        )

        logger.info("[%s] Applied style '%s'", self.name, style_name)
        return result

    # ---------------- Storage Interaction ---------------- #
    def store_result(self, storage_manager, result: Any, name: str):
        """
        Store a result object in the StorageManager using the appropriate save method.
        """
        # Use the generic StorageManager.save(obj_type, name, obj) method
        # to avoid relying on dynamically-named save_* methods.
        obj_type = self.result_type.__name__.lower()
        try:
            storage_manager.save(obj_type, name, result)
        except AttributeError:
            # If StorageManager doesn't implement generic save, raise a clear error
            raise AttributeError(
                "StorageManager does not implement 'save(obj_type, name, obj)'."
            )

        logger.info(
            "[%s] Stored %s '%s' in StorageManager",
            self.name,
            self.result_type.__name__,
            name,
        )

    # ---------------- Abstract Work ---------------- #
    @abstractmethod
    def work(self, *args, **kwargs):
        """
        Abstract method that defines how the agent performs its task.
        Should typically call apply_style().
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}>"
