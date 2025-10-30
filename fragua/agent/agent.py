"""
Agent class in Fragua.
Agents can take a role to work like a Miner, Blacksmith, or Transporter.
"""

from __future__ import annotations
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Any, Optional, TypeVar, ParamSpec
import pandas as pd

from fragua.agent.store_manager import StoreManager
from fragua.style.style import Style
from fragua.store.storage import Storage
from fragua.store.storage_types import get_storage, list_storages
from fragua.utils.logger import get_logger
from fragua.utils.metrics import add_metadata_to_storage, generate_metadata

StyleT = TypeVar("StyleT", bound=Style[Any, Any])
P = ParamSpec("P")
R = TypeVar("R")
SelfT = TypeVar("SelfT")

logger = get_logger(__name__)


class Agent(ABC):  # pylint: disable=too-many-instance-attributes
    """Agent class for ETL agents."""

    def __init__(
        self,
        name: str,
        store_manager: StoreManager | None = None,
    ):
        self.name: str = name
        self.store_manager = store_manager
        self.role: str
        self._operations: list[dict[str, Any]] = []
        self.action: str
        self.storage_type: str

        logger.debug(
            "Initialized Agent '%s' with role '%s' (action=%s, storage=%s)",
            self.name,
            self.role,
            self.action,
            self.storage_type,
        )

    # ----------------- Helpers ----------------- #
    def _determine_origin_name(self, origin: Any) -> Optional[str]:
        """Extract a meaningful origin name for operation metadata."""
        origin_name = None
        match origin:
            case Storage():
                origin_name = origin.__class__.__name__
                logger.debug("Detected Storage origin: %s", origin_name)
            case str() | Path():
                origin_name = Path(origin).name
                logger.debug("Detected file path origin: %s", origin_name)
            case _:
                if hasattr(origin, "path") and isinstance(origin.path, (str, Path)):
                    origin_name = Path(origin.path).name
                    logger.debug(
                        "Detected object with .path attribute: %s", origin_name
                    )
                elif hasattr(origin, "data") and isinstance(origin.data, pd.DataFrame):
                    origin_name = "DataFrame"
                    logger.debug("Detected object with .data as DataFrame")
                else:
                    logger.debug("Origin type not recognized; returning None")
        return origin_name

    # ----------------- Metadata----------------- #
    def _generate_operation_metadata(
        self, style_name: str, storage: Storage[Any], origin: Any
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

    # ----------------- Create Storage ----------------- #
    def create_storage(self, data: Any) -> Storage[Any]:
        """Convert raw style output into the appropriate storage object using registry."""
        try:
            storage_cls = get_storage(self.storage_type)
        except KeyError as exc:
            raise TypeError(
                f"Result type '{self.storage_type}' is not a valid registered storage"
            ) from exc
        return storage_cls(data=data)

    # ----------------- Store Manager Interaction ----------------- #
    def store_result(
        self,
        storage_manager: Any,
        storage: Storage[Any],
        storage_name: str | None = None,
    ) -> None:
        """Store a Storage object via a StoreManager."""
        storage_type_lower = storage.__class__.__name__.lower()

        if storage_type_lower not in list_storages():
            raise ValueError(
                f"'{storage_type_lower}' is not a valid registered storage type"
            )

        if storage_name is None:
            existing_count = len(storage_manager.store.data)
            storage_name = f"{storage_type_lower}_{existing_count + 1}"

        storage_manager.add(
            storage=storage,
            storage_type=storage_type_lower,
            storage_name=storage_name,
            agent_name=self.name,
        )

        logger.debug(
            "[%s] Stored %s as '%s' via store manager '%s'",
            self.name,
            storage_type_lower,
            storage_name,
            storage_manager.name if hasattr(storage_manager, "name") else "unknown",
        )

    # ----------------- Work Pipeline ----------------- #
    @abstractmethod
    def work(self, /, style_name: str, **kwargs: Any) -> None:
        """Execute the agent's task using the action and style defined by its role."""
