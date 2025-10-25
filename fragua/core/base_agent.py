"""
Base class for all ETL agents in Fragua.

Defines the common interface and shared behavior for
agents Miner, Blacksmith, and Transporter.
"""

from abc import ABC
from datetime import datetime, timezone
from pathlib import Path
from typing import (
    Any,
    Dict,
    Type,
    TypeVar,
    Generic,
    Optional,
    cast,
)

import pandas as pd
from fragua.utils.logger import get_logger
from fragua.core.base_style import BaseStyle
from fragua.core.base_storage import BaseStorage
from fragua.core.base_params import BaseParams
from fragua.store.wagon import Wagon
from fragua.store.box import Box
from fragua.store.container import Container
from fragua.agents.store_manager import StoreManager
from fragua.utils.metrics import (
    add_metadata_to_storage,
    generate_metadata,
    determine_storage_type,
)


StyleT = TypeVar("StyleT", bound=BaseStyle[Any, Any])
StorageT = TypeVar("StorageT", bound=BaseStorage[Any])


logger = get_logger(__name__)


class BaseAgent(ABC, Generic[StyleT, StorageT]):
    """Abstract base class for ETL agents with built-in support
    for learning and applying registered styles."""

    style_registry: Dict[str, Type[StyleT]] = {}
    storage_type: Optional[Type[StorageT]] = None

    def __init__(self, name: str):
        self.name: str = name
        self.known_styles: Dict[str, StyleT] = {}
        self.learned_styles: Dict[str, dict[Any, Any]] = {}
        self._operations: list[dict[Any, Any]] = []

    # ----------------- Helpers ----------------- #
    def _determine_input_name(self, input_obj: Any) -> str | None:
        """Extract a meaningful input name for the operation metadata with lazy logging."""
        result = None  # Store the determined name

        match input_obj:
            # Direct BaseStorage (Wagon, Box, Container)
            case BaseStorage():
                result = determine_storage_type(input_obj)
                logger.debug("Detected BaseStorage input: %s", result)

            # Path or string path
            case str() | Path():
                result = Path(input_obj).name
                logger.debug("Detected file path input: %s", result)

            # Fallback cases
            case _:
                if hasattr(input_obj, "path") and isinstance(
                    input_obj.path, (str, Path)
                ):
                    result = Path(input_obj.path).name
                    logger.debug("Detected object with .path attribute: %s", result)
                elif hasattr(input_obj, "data") and isinstance(
                    input_obj.data, BaseStorage
                ):
                    result = input_obj.data.name
                    logger.debug(
                        "Detected object with .data as BaseStorage: %s", result
                    )
                elif hasattr(input_obj, "data") and isinstance(
                    input_obj.data, pd.DataFrame
                ):
                    result = "data"
                    logger.debug("Detected object with .data as DataFrame")
                elif hasattr(input_obj, "name"):
                    result = str(input_obj.name)
                    logger.debug("Detected object with .name attribute: %s", result)
                else:
                    logger.debug("Input type not recognized; returning None")

        return result

    def _generate_operation_metadata(
        self, style_name: str, output_obj: StorageT, input_obj: Any
    ):
        """Generate metadata from operation"""
        input_name = self._determine_input_name(input_obj)
        metadata = generate_metadata(
            output_obj,
            metadata_type="operation",
            input_name=input_name,
            style_name=style_name,
        )
        add_metadata_to_storage(output_obj, metadata)

    # ----------------- Operations ----------------- #
    def get_operations(self) -> pd.DataFrame:
        """Return a DataFrame with all recorded operations."""
        logger.debug(
            "[%s] Returning %d recorded operations",
            self.name,
            len(self._operations),
        )
        return pd.DataFrame(self._operations)

    # ----------------- Learning ----------------- #
    def learn_style(self, style_instance: StyleT) -> None:
        """Register a style instance with this agent."""
        self.known_styles[style_instance.style_name] = style_instance
        self.learned_styles[style_instance.style_name] = {
            "class": style_instance.__class__.__name__,
            "learned_at": datetime.now(timezone.utc),
        }
        logger.info("[%s] Learned style '%s'", self.name, style_instance.style_name)

    def learn_style_by_name(self, name: str) -> None:
        """Create and learn a style dynamically from the registry."""
        if name not in self.style_registry:
            raise ValueError(f"No style registered under name '{name}'")
        style_cls = self.style_registry[name]
        instance = style_cls(style_name=name)
        self.learn_style(instance)

    # ----------------- Normalize Data ----------------- #
    def normalize_input_data(self, input_data: Any) -> Any:
        """
        Convert input data into a format compatible with BaseStyle.

        - If input is BaseStorage, return its `.data`.
        - If input is DataFrame or BaseParams, return as is.
        - Otherwise, return the original object.
        """

        if isinstance(input_data, BaseStorage):
            if input_data.data is None:
                raise ValueError(f"{input_data.name} has no data to process")
            agent_name = getattr(self, "name", "unknown")
            logger.debug("[%s] Normalized input from BaseStorage", agent_name)
            return input_data.data

        if isinstance(input_data, pd.DataFrame):
            agent_name = getattr(self, "name", "unknown")
            logger.debug("[%s] Input is already a DataFrame", agent_name)
            return input_data

        if isinstance(input_data, BaseParams):
            agent_name = getattr(self, "name", "unknown")
            logger.debug("[%s] Input is BaseParams", agent_name)
            return input_data

        agent_name = getattr(self, "name", "unknown")
        logger.debug("[%s] Input normalization returned original data", agent_name)
        return input_data

    # ----------------- Create Storage ----------------- #
    def create_storage(self, data: Any) -> StorageT:
        """Convert raw style output into the appropriate storage object."""

        if self.storage_type is None:
            raise TypeError(
                f"Cannot wrap result: {self.__class__.__name__} has no result_type defined."
            )

        type_name = self.storage_type.__name__.lower()
        storage_obj: Optional[BaseStorage[Any]] = None

        storage_obj: Optional[BaseStorage[Any]] = None

        match type_name:
            case "wagon":
                storage_obj = Wagon(data=data)
            case "box":
                storage_obj = Box(data=data)
            case "container":
                storage_obj = Container(data=data)
            case _:
                raise TypeError(
                    f"Result type '{self.storage_type.__name__}' is not a valid storage type"
                )

        return cast(StorageT, storage_obj)

    # ----------------- Apply Style ----------------- #
    def apply_style(self, style_name: str, data: Any) -> StorageT:
        """Apply a learned style to data."""
        if style_name not in self.known_styles:
            raise ValueError(f"Style '{style_name}' not learned")

        style = self.known_styles[style_name]
        stylized_data = style.use(data)

        logger.info("[%s] Applied style '%s'", self.name, style_name)
        return stylized_data

    # ----------------- Store Manager Interaction ----------------- #
    def store_result(
        self, storage_manager: StoreManager[Any], storage: StorageT, storage_name: str
    ) -> None:
        """Store a storage(Wagon, Box, Container) via an store manager."""

        storage_type = determine_storage_type(storage)

        if storage_type not in ["wagon", "box", "container"]:
            raise ValueError("Result type is not a valid storage type")

        storage_manager.save(storage_type, storage, storage_name, agent_name=self.name)

    # ----------------- Work Pipeline ----------------- #
    def work(self, style_name: str, data: Any) -> StorageT:
        """Method that defines how the agent performs its task."""

        normalized_data = self.normalize_input_data(data)
        stylized_data = self.apply_style(style_name, normalized_data)
        storage = self.create_storage(stylized_data)

        self._generate_operation_metadata(
            style_name=style_name, output_obj=storage, input_obj=data
        )

        return storage

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
