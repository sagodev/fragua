"""
Base class for all ETL agents in Fragua.

Defines the common interface and shared behavior for
agents Miner, Blacksmith, and Transporter.
"""

from abc import ABC
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Type, TypeVar, Generic, Optional, cast

import pandas as pd
from fragua.utils.logger import get_logger
from fragua.core.base_style import BaseStyle
from fragua.core.base_storage import BaseStorage
from fragua.core.base_params import BaseParams
from fragua.store.wagon import Wagon
from fragua.store.box import Box
from fragua.store.container import Container
from fragua.agents.store_manager import StoreManager, AllowedStorage
from fragua.utils.metrics import (
    add_metadata_to_storage,
    generate_metadata,
    determine_storage_type,
)


StyleT = TypeVar("StyleT", bound=BaseStyle[Any, Any])
StorageT = TypeVar("StorageT", bound=AllowedStorage)


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
    def _determine_origin_name(self, origin: Any) -> str | None:
        """Extract a meaningful origin name for the operation metadata with lazy logging."""

        origin_name = None

        match origin:
            # Direct BaseStorage (Wagon, Box, Container)
            case BaseStorage():
                origin_name = str(determine_storage_type(origin))
                logger.debug("Detected BaseStorage origin: %s", origin_name)

            # Path or string path
            case str() | Path():
                origin_name = Path(origin).name
                logger.debug("Detected file path origin: %s", origin_name)

            # Fallback cases
            case _:
                # BaseParams type
                if hasattr(origin, "path") and isinstance(origin.path, (str, Path)):
                    origin_name = Path(origin.path).name
                    logger.debug(
                        "Detected object with .path attribute: %s", origin_name
                    )
                # Dataframe
                elif hasattr(origin, "data") and isinstance(origin.data, pd.DataFrame):
                    origin_name = "dataframe"
                    logger.debug("Detected object with .data as DataFrame")
                else:
                    logger.debug("Origin type not recognized; returning None")

        return origin_name

    def _generate_operation_metadata(
        self, style_name: str, storage: StorageT, origin: Any
    ) -> None:
        """Generate metadata from operation"""

        origin_name = self._determine_origin_name(origin)

        metadata = generate_metadata(
            storage=storage,
            metadata_type="operation",
            origin_name=origin_name,
            style_name=style_name,
        )
        add_metadata_to_storage(storage, metadata)

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
    def learn_style(self, *styles: StyleT) -> None:
        """Register one or multiple style instances with this agent."""
        for style in styles:
            self.known_styles[style.style_name] = style
            self.learned_styles[style.style_name] = {
                "class": style.__class__.__name__,
                "learned_at": datetime.now(timezone.utc),
            }
            logger.info("[%s] Learned style '%s'", self.name, style.style_name)

    def learn_style_by_name(self, *style_names: str) -> None:
        """Create and learn one or multiple styles dynamically from the registry."""
        for name in style_names:
            if name not in self.style_registry:
                raise ValueError(f"No style registered under name '{name}'")

            style_cls = self.style_registry[name]
            style = style_cls(style_name=name)
            self.learn_style(style)

    # ----------------- Normalize Data ----------------- #
    def normalize_origin_data(self, origin: Any) -> Any:
        """
        Convert origin data into a format compatible with BaseStyle.

        - If origin is BaseStorage, return its `.data`.
        - If origin is DataFrame or BaseParams, return as is.
        - Otherwise, return the original object.
        """

        if isinstance(origin, BaseStorage):
            if origin.data is None:
                raise ValueError(
                    f"the {str(determine_storage_type(origin))} has no data to process"
                )
            agent_name = getattr(self, "name", "unknown")
            logger.debug("[%s] Normalized origin from BaseStorage", agent_name)
            return origin.data

        if isinstance(origin, pd.DataFrame):
            agent_name = getattr(self, "name", "unknown")
            logger.debug("[%s] Origin is already a DataFrame", agent_name)
            return origin

        if isinstance(origin, BaseParams):
            agent_name = getattr(self, "name", "unknown")
            logger.debug("[%s] Origin is BaseParams", agent_name)
            return origin

        agent_name = getattr(self, "name", "unknown")
        logger.debug("[%s] Origin normalization returned original data", agent_name)
        return origin

    # ----------------- Create Storage ----------------- #
    def create_storage(self, data: Any) -> StorageT:
        """Convert raw style output into the appropriate storage object."""

        if self.storage_type is None:
            raise TypeError(
                f"Cannot wrap result: {self.__class__.__name__} has no result_type defined."
            )

        type_name = self.storage_type.__name__.lower()
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
    def apply_style(self, style_name: str, data: Any) -> Any:
        """Apply a learned style to data."""
        if style_name not in self.known_styles:
            raise ValueError(f"Style '{style_name}' not learned")

        style = self.known_styles[style_name]
        stylized_data = style.use(data)

        logger.info("[%s] Applied style '%s'", self.name, style_name)
        return stylized_data

    # ----------------- Store Manager Interaction ----------------- #
    def store_result(
        self,
        storage_manager: StoreManager,
        storage: StorageT,
        storage_name: str,
    ) -> None:
        """Store a storage(Wagon, Box, Container) via an store manager."""

        storage_type = determine_storage_type(storage)

        if storage_type not in ["wagon", "box", "container"]:
            raise ValueError("Result type is not a valid storage type")

        storage_manager.save(
            storage=storage,
            storage_name=storage_name,
            agent_name=self.name,
        )

    # ----------------- Work Pipeline ----------------- #
    def work(self, style_name: str, data: Any) -> StorageT:
        """Method that defines how the agent performs its task."""

        normalized_data = self.normalize_origin_data(data)
        stylized_data = self.apply_style(style_name, normalized_data)
        storage = self.create_storage(stylized_data)

        self._generate_operation_metadata(
            style_name=style_name, storage=storage, origin=data
        )

        return storage

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
