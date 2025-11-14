"""
Agent class in Fragua.
Agents can take a role to work like a Miner, Blacksmith, or Transporter.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Union, Generic
from datetime import datetime, timezone

import pandas as pd

from fragua.params.params import Params, ParamsT
from fragua.storages.storage import Storage
from fragua.storages.storage_types import Box, Wagon, STORAGE_CLASSES


from fragua.utils.logger import get_logger
from fragua.utils.metrics import add_metadata_to_storage, generate_metadata

if TYPE_CHECKING:
    from fragua.environments.environment import Environment

logger = get_logger(__name__)


class Agent(ABC, Generic[ParamsT]):  # pylint: disable=too-many-instance-attributes
    """Agent class for ETL agents using shared Environment registries."""

    def __init__(
        self,
        name: str,
        environment: Environment,
    ) -> None:
        self.name: str = name
        self.environment: Environment = environment
        self.role: str
        self.action: str
        self.storage_type: str
        self._operations: list[dict[str, Any]] = []

    # ----------------- Registry Access ----------------- #

    def get_registred_class(self, reg: str, style: str, action: str) -> Any:
        """Retrieve a class object from environment registries."""
        registry = self.environment.registries.get(reg, {})
        for a_name, styles in registry.items():
            if a_name == action:
                for s_name, cls in styles.items():
                    if s_name == style:
                        return cls
        raise KeyError(f"No class found for registry '{reg}'.")

    @property
    def warehouse_manager(self):
        """Access the shared warehouse manager from the environment."""
        return self.environment.get_manager()

    # ----------------- Helpers ----------------- #
    def _determine_origin_name(self, origin: Any) -> Optional[str]:
        origin_name = None
        match origin:
            case Storage():
                origin_name = origin.__class__.__name__
            case str() | Path():
                origin_name = Path(origin).name
            case _:
                if hasattr(origin, "path") and isinstance(origin.path, (str, Path)):
                    origin_name = Path(origin.path).name
                elif hasattr(origin, "data") and isinstance(origin.data, pd.DataFrame):
                    origin_name = "DataFrame"
        return origin_name

    def _generate_storage_name(self, style_name: str) -> str:
        return f"{style_name}_{self.action}_data"

    # ----------------- Metadata ----------------- #
    def _generate_operation_metadata(
        self, style_name: str, storage: Storage[Any], origin: Any
    ) -> None:
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
        return pd.DataFrame(self._operations)

    def _add_operation(self, style: str, params_instance: Params) -> None:
        self._operations.append(
            {
                "action": self.action,
                "style_name": style,
                "timestamp": datetime.now(timezone.utc),
                "params": params_instance,
            }
        )

    # ----------------- Create Storage ----------------- #
    def create_storage(self, data: Any) -> Storage[Any]:
        """Convert raw style output into the appropriate storage object."""
        storage_cls = STORAGE_CLASSES.get(self.storage_type)
        if not storage_cls:
            raise TypeError(f"Invalid storage type: '{self.storage_type}'.")
        return (
            storage_cls(data=data)
            if self.storage_type != "Container"
            else storage_cls()
        )

    # ----------------- Store Interaction ----------------- #
    def add_to_warehouse(
        self, storage: Storage[Any], storage_name: str | None = None
    ) -> None:
        """Store an object using the shared WarehouseManager."""

        self.warehouse_manager.add(
            storage=storage, storage_name=storage_name, agent_name=self.name
        )

    def get_from_warehouse(
        self,
        storage_name: str | None,
    ) -> Union[
        Wagon,
        Box,
    ]:
        """Get storage from warehouse by a given storage name."""

        if storage_name is None:
            raise TypeError("Missing required attribute: storage_name.")

        storage = self.warehouse_manager.get(
            storage_name=storage_name, agent_name=self.name
        )

        if storage is None:
            raise TypeError("Storage not found in warehouse.")

        if not isinstance(storage, Union[Wagon, Box]):
            raise TypeError("Storage is not a Wagon or Box.")

        return storage

    def auto_store(
        self, style: str, storage: Storage[Any], save_as: str | None
    ) -> None:
        """Add automatically an storage to warehouse."""
        name = save_as or self._generate_storage_name(style)
        self.add_to_warehouse(storage, name)

    # ----------------- Work Pipeline ----------------- #
    def _execute_workflow(
        self,
        style: str,
        save_as: str | None = None,
        params: Params | None = None,
        **kwargs: Any,
    ) -> None:
        """Common workflow for agents using environment registries."""

        style = style.lower()

        if params is None:
            params_cls = self.get_registred_class("params", style, self.action)
            params_instance = params_cls(**kwargs)
        else:
            params_instance = params

        style_cls = self.get_registred_class("styles", style, self.action)
        stylized_data = style_cls(style).use(params_instance)
        storage = self.create_storage(stylized_data)

        self._generate_operation_metadata(style, storage, params_instance)
        self._add_operation(style, params_instance)
        self.auto_store(style, storage, save_as)

    # ----------------- Abstract ----------------- #
    @abstractmethod
    def work(
        self,
        /,
        style: str,
        apply_to: str | list[str] | None = None,
        save_as: str | None = None,
        params: ParamsT | None = None,
        **kwargs: Any,
    ) -> None:
        """Execute the agent's task using the action and style defined by its role."""
        self._execute_workflow(style, save_as, params, **kwargs)
