"""
Agent class in Fragua.
Agents can take a role to work like a Miner, Blacksmith, or Transporter.
"""

from __future__ import annotations
from abc import abstractmethod, ABC
from pathlib import Path
from typing import Any, Mapping, Optional, TypeVar, ParamSpec, Union
import pandas as pd

from fragua.agents.store_manager import StoreManager
from fragua.params.params import PARAMS_REGISTRY, Params
from fragua.style.style import STYLE_REGISTRY, Style
from fragua.store.storage import Storage
from fragua.store.storage_types import Box, Wagon, get_storage
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
        store_manager: StoreManager,
    ):
        self.name: str = name
        self.store_manager = store_manager
        self.role: str
        self._operations: list[dict[str, Any]] = []
        self.action: str
        self.storage_type: str

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

    def _generate_storage_name(self, style_name: str) -> str:
        """Generate a name for storage from action and style."""
        storage_name: str = f"{style_name}_{self.action}_data"
        return storage_name

    def _get_params(self, style: str, **kwargs: Any) -> Params:
        """Get params instance by a given agent role and style."""
        params_cls: type[Params] | None = PARAMS_REGISTRY.get((self.role, style))
        if not params_cls:
            raise ValueError(f"No Params class registered for ({self.role}, {style})")

        return params_cls(**kwargs)

    def _get_style(self, style: str) -> Style[Any, Any]:
        """Get style instance by a given agent role and style."""
        style_key = (self.action, style)
        style_cls: type[Style[Any, Any]] | None = STYLE_REGISTRY.get(style_key)
        if not style_cls:
            raise ValueError(f"No Style class registered for {style_key}")

        return style_cls(style_name=style)

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
        """Return a DataFrame with all recorded operations done by the agent."""
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

        if self.storage_type == "Container":
            return storage_cls()

        return storage_cls(data=data)

    # ----------------- Store Manager Interaction ----------------- #
    def add_to_store(
        self,
        storage: Storage[Any],
        storage_name: str | None = None,
    ) -> None:
        """Store a Storage object via a StoreManager."""

        self.store_manager.add(
            storage=storage,
            storage_name=storage_name,
            agent_name=self.name,
        )

    def get_from_store(self, storage_name: str | None) -> Union[
        Optional[Union[Wagon, Box]],
        Mapping[str, Union[Wagon, Box]],
        Mapping[str, Mapping[str, Union[Wagon, Box]]],
    ]:
        """Get data storage from store by a given storage name."""

        if storage_name is None:
            raise TypeError("Missing required atribute: storage_name.")

        storage = self.store_manager.get(
            storage_name=storage_name, agent_name=self.name
        )

        if self.role == "haulier":
            return storage

        if isinstance(storage, (Wagon, Box)):
            df = storage.data
        elif isinstance(storage, Mapping):
            first_value = next(iter(storage.values()))
            if isinstance(first_value, (Wagon, Box)):
                df = first_value.data
            else:
                raise TypeError("Invalid nested mapping structure in store.")
        else:
            raise TypeError(f"Unexpected data type: {type(storage).__name__}")
        return df

    # ----------------- Work Pipeline ----------------- #
    @abstractmethod
    def work(
        self,
        /,
        style: str,
        **kwargs: Any,
    ) -> None:
        """Execute the agent's task using the action and style defined by its role."""
