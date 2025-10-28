"""
Agent class in Fragua.
Agents can take a role to work like a Miner, Blacksmith, Transporter, or Master.
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Optional, TypeVar, cast

import pandas as pd
from fragua.utils.logger import get_logger
from fragua.core.style import Style, STYLE_REGISTRY
from fragua.core.storage import Storage, get_storage, list_storages
from fragua.core.params import PARAMS_REGISTRY, Params
from fragua.utils.metrics import add_metadata_to_storage, generate_metadata
from fragua.agents.agent_roles import get_role, MasterRole

StyleT = TypeVar("StyleT", bound=Style[Any, Any])

logger = get_logger(__name__)


class Agent:
    """Agent class for ETL agents."""

    def __init__(self, role: str, name: str):
        self.role: str = role.lower()
        self.name: str = name
        self._operations: list[dict[str, Any]] = []

        try:
            role_cfg = get_role(self.role)
        except KeyError as exc:
            raise ValueError(f"No role registered with name '{role}'") from exc

        self.action: str = role_cfg["action"]
        self.storage_type: str = role_cfg["storage_type"]
        self.allowed_functions: tuple[str, ...] = role_cfg.get("allowed_functions", ())

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
    def create_storage(self, data: Any, style_name: str) -> Storage[Any]:
        """
        Convert raw style output into the appropriate storage object using registry.
        For master, deduce storage_type automatically based on style_name prefix.
        """
        storage_type = self.storage_type

        if self.role == "master":
            prefix = style_name.split("_")[0]
            storage_type = MasterRole.style_prefix_to_storage.get(prefix, "Wagon")

        try:
            storage_cls = get_storage(storage_type)
        except KeyError as exc:
            raise TypeError(
                f"Result type '{storage_type}' is not a valid registered storage"
            ) from exc

        return storage_cls(data=data)

    # ----------------- Store Manager Interaction ----------------- #
    def store_result(
        self,
        storage_manager: Any,
        storage: Storage[Any],
        storage_name: str,
    ) -> None:
        """Store a storage (Wagon, Box, Container) via a store manager."""
        storage_type = storage.__class__.__name__
        if storage_type not in list_storages():
            raise ValueError(f"'{storage_type}' is not a valid registered storage type")
        storage_manager.save(
            storage=storage,
            storage_name=storage_name,
            agent_name=self.name,
        )

    # ----------------- Work Pipeline ----------------- #
    def work(self, style_name: str, **kwargs: Any) -> Storage[Any]:
        """Execute the agent's task using the action and style defined by its role."""

        # ----------------- Deduce action & storage for master -----------------
        if self.role == "master":
            prefix = style_name.split("_")[0]
            self.action = MasterRole.style_prefix_to_action.get(prefix, "mine")
            self.storage_type = MasterRole.style_prefix_to_storage.get(prefix, "Wagon")

        # ----------------- PARAMS fallback -----------------
        params_cls: type[Params] | None = PARAMS_REGISTRY.get((self.role, style_name))
        if not params_cls and self.role == "master":
            for (_, s), params_class in PARAMS_REGISTRY.items():
                if s == style_name:
                    params_cls = params_class
                    break
        if not params_cls:
            raise ValueError(
                f"No Params class registered for ({self.role}, {style_name})"
            )

        params_instance = params_cls(**kwargs)

        # ----------------- STYLE fallback -----------------
        style_key = (self.action, style_name)
        style_cls: type[Style[Any, Any]] | None = STYLE_REGISTRY.get(
            (self.action, style_name)
        )
        if not style_cls and self.role == "master":
            for (_, s), style_class in STYLE_REGISTRY.items():
                if s == style_name:
                    style_cls = style_class
                    break
        if not style_cls:
            raise ValueError(f"No Style class registered for {style_key}")

        # ----------------- Execute style -----------------
        style_instance = style_cls(style_name=style_name)
        stylized_data = style_instance.use(params_instance)
        storage = self.create_storage(stylized_data, style_name=style_name)

        self._generate_operation_metadata(
            style_name=style_name,
            storage=storage,
            origin=params_instance,
        )

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
        return f"<Agent name={self.name} role={self.role}>"
