"""
Base class for all ETL agents in Fragua.

Defines the common interface and shared behavior for
agents like Miner, Blacksmith, and Transporter.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Type, TypeVar, Generic, TYPE_CHECKING, Optional
import pandas as pd
from fragua.utils.logger import get_logger
from fragua.core.base_style import BaseStyle

if TYPE_CHECKING:
    from fragua.agents.store.storage_manager import StorageManager

# Generic type variables
StyleT = TypeVar("StyleT", bound=BaseStyle)
ResultT = TypeVar("ResultT")

logger = get_logger("BaseAgent")


class BaseAgent(ABC, Generic[StyleT, ResultT]):
    """
    Abstract base class for ETL agents with built-in support
    for learning and applying registered styles.
    """

    # Subclasses must override these
    style_registry: Dict[str, Type[StyleT]] = {}
    result_type: Optional[Type[ResultT]] = None
    metadata_table_name: str = "operations"

    def __init__(self, name: str):
        """
        Initialize the agent with a given name.

        Args:
            name (str): The name of the agent.
        """
        self.name = name
        self.known_styles: Dict[str, StyleT] = {}
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
    def learn_style(self, style_instance: StyleT) -> None:
        """
        Register a style instance and record its metadata.

        Args:
            style_instance (StyleT): Instance of a Style subclass to register
        """
        self.known_styles[style_instance.style_name] = style_instance
        self.metadata["learned_styles"][style_instance.style_name] = {
            "class": style_instance.__class__.__name__,
            "learned_at": datetime.now(timezone.utc),
        }
        logger.info("[%s] Learned style '%s'", self.name, style_instance.style_name)

    def learn_style_by_name(self, name: str) -> None:
        """
        Create and learn a style dynamically from the registry.
        The style is registered with the same name used to look it up.

        Args:
            name (str): Name of the style to create and register

        Raises:
            ValueError: If style name is not in registry
        """
        if name not in self.style_registry:
            logger.error("[%s] No style registered under '%s'", self.name, name)
            raise ValueError(f"No style registered under name '{name}'")

        style_cls = self.style_registry[name]
        instance = style_cls(style_name=name)
        self.learn_style(instance)

    # ---------------- Working ---------------- #
    def apply_style(self, style_name: str, data: Any) -> ResultT:
        """
        Apply a learned style and record operation metadata.

        Args:
            style_name: Name of the style to apply
            data: Input data for the style

        Returns:
            ResultT: Result of applying the style

        Raises:
            ValueError: If style is not learned
            TypeError: If style returns wrong type
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
                f"Style '{style_name}' must return {self.result_type.__name__}, "
                f"got {type(result).__name__}"
            )

        # Safely extract metadata
        result_name = getattr(result, "name", None)
        result_data = getattr(result, "data", None)
        result_shape = getattr(result_data, "shape", (None, None))
        style_metadata = getattr(style, "metadata", {})
        style_checksum = (
            style_metadata.get("checksum") if isinstance(style_metadata, dict) else None
        )

        new_row = {
            "style_name": style_name,
            "timestamp": datetime.now(timezone.utc),
            "output_name": result_name,
            "rows": result_shape[0],
            "columns": result_shape[1],
            "checksum": style_checksum,
        }
        self.metadata[self.metadata_table_name] = pd.concat(
            [self.metadata[self.metadata_table_name], pd.DataFrame([new_row])],
            ignore_index=True,
        )

        logger.info("[%s] Applied style '%s'", self.name, style_name)
        return result

    # ---------------- Storage Interaction ---------------- #
    def store_result(
        self, storage_manager: "StorageManager", result: ResultT, name: str
    ) -> None:
        """
        Store a result object in the StorageManager using the appropriate save method.

        Args:
            storage_manager: The StorageManager instance to store the result in
            result: The result object to store (must match ResultT type)
            name: Name to store the result under

        Raises:
            AttributeError: If StorageManager doesn't implement required save method
        """
        # Use the generic StorageManager.save(obj_type, name, obj) method
        # to avoid relying on dynamically-named save_* methods.
        obj_type = self.result_type.__name__.lower()
        try:
            storage_manager.save(obj_type, name, result)
        except AttributeError as exc:
            raise AttributeError(
                "StorageManager does not implement 'save(obj_type, name, obj)'."
            ) from exc

        logger.info(
            "[%s] Stored %s '%s' in StorageManager",
            self.name,
            self.result_type.__name__,
            name,
        )

    # ---------------- Abstract Work ---------------- #

    @abstractmethod
    def work(self, *args: Any, **kwargs: Any) -> ResultT:
        """
        Abstract method that defines how the agent performs its task.
        Should typically call apply_style().

        Args:
            *args: Variable positional arguments
            **kwargs: Variable keyword arguments

        Returns:
            ResultT: The result type specific to this agent subclass
        """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
