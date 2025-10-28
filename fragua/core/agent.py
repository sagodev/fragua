"""
Agent class in Fragua.
Agents can take a rol to work like a Miner, Blacksmith or Transporter.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Optional, TypeVar

import pandas as pd
from fragua.utils.logger import get_logger
from fragua.core.base_style import BaseStyle, STYLE_REGISTRY
from fragua.core.base_storage import BaseStorage
from fragua.core.base_params import PARAMS_REGISTRY
from fragua.utils.metrics import (
    add_metadata_to_storage,
    generate_metadata,
    determine_storage_type,
)

StyleT = TypeVar("StyleT", bound=BaseStyle[Any, Any])

AGENT_ROLES: dict[str, dict[str, str]] = {
    "miner": {"action": "mine", "storage": "wagon"},
    "blacksmith": {"action": "forge", "storage": "box"},
    "transporter": {"action": "deliver", "storage": "container"},
}

logger = get_logger(__name__)


class Agent:
    """Agent class for ETL agents."""

    def __init__(self, rol: str, name: str):
        self.rol: str = rol.lower()
        self.name: str = name
        self._operations: list[dict[str, Any]] = []

        if self.rol not in AGENT_ROLES:
            raise ValueError(f"No role registered with name '{rol}'")

        self.action: str = AGENT_ROLES[self.rol]["action"]
        self.storage_type: str = AGENT_ROLES[self.rol]["storage"]

    # ----------------- Helpers ----------------- #
    def _determine_origin_name(self, origin: Any) -> Optional[str]:
        """Extract a meaningful origin name for operation metadata."""

        origin_name = None

        match origin:
            case BaseStorage():
                origin_name = str(determine_storage_type(origin))
                logger.debug("Detected BaseStorage origin: %s", origin_name)
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
                    origin_name = "dataframe"
                    logger.debug("Detected object with .data as DataFrame")
                else:
                    logger.debug("Origin type not recognized; returning None")

        return origin_name

    def _generate_operation_metadata(
        self, style_name: str, storage: BaseStorage[Any], origin: Any
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
    def create_storage(self, data: Any):
        """Convert raw style output into the appropriate storage object."""
        from fragua.store import Wagon, Box, Container

        match self.storage_type:
            case "wagon":
                return Wagon(data=data)
            case "box":
                return Box(data=data)
            case "container":
                return Container(data=data)
            case _:
                raise TypeError(f"Result type '{self.storage_type}' is not valid")

    # ----------------- Store Manager Interaction ----------------- #
    def store_result(
        self,
        storage_manager: Any,
        storage: BaseStorage[Any],
        storage_name: str,
    ) -> None:
        """Store a storage(Wagon, Box, Container) via a store manager."""
        st_type = determine_storage_type(storage)
        if st_type not in ["wagon", "box", "container"]:
            raise ValueError("Result type is not a valid storage type")

        storage_manager.save(
            storage=storage,
            storage_name=storage_name,
            agent_name=self.name,
        )

    # ----------------- Work Pipeline ----------------- #
    def work(self, style_name: str, **kwargs: Any) -> BaseStorage[Any]:
        """
        Execute the agent's task using the action and style defined by the agent's role.
        Resolves Params and Style classes from PARAMS_REGISTRY and STYLE_REGISTRY.
        """
        # --- Resolve Params class ---
        params_cls = PARAMS_REGISTRY.get((self.rol, style_name))
        if not params_cls:
            raise ValueError(
                f"No Params class registered for ({self.rol}, {style_name})"
            )
        params_instance = params_cls(**kwargs)

        # --- Resolve Style class ---
        style_key = (self.action, style_name)
        style_cls = STYLE_REGISTRY.get(style_key)
        if not style_cls:
            raise ValueError(f"No Style class registered for {style_key}")
        style_instance = style_cls(style_name=style_name)

        # --- Apply style ---
        stylized_data = style_instance.use(params_instance)

        # --- Wrap result in storage ---
        storage = self.create_storage(stylized_data)

        # --- Add operation metadata ---
        self._generate_operation_metadata(
            style_name=style_name,
            storage=storage,
            origin=params_instance,
        )

        # --- Record operation for history ---
        self._operations.append(
            {
                "action": self.action,
                "style_name": style_name,
                "timestamp": datetime.now(timezone.utc),
                "params": params_instance,
            }
        )

        logger.info(
            "[%s] Executed '%s' action with style '%s'",
            self.name,
            self.action,
            style_name,
        )
        return storage

    def __repr__(self) -> str:
        return f"<Agent name={self.name} rol={self.rol}>"
