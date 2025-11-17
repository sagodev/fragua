"""
Agent class in Fragua.
Agents can take a role to work like a Miner, Blacksmith, or Transporter.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Generic
from datetime import datetime, timezone

import pandas as pd

from fragua.agents.warehouse_manager import WarehouseManager
from fragua.params.params import Params, ParamsT
from fragua.storages.storage import Storage
from fragua.storages.storage_types import Box, STORAGE_CLASSES


from fragua.utils.logger import get_logger
from fragua.utils.metrics import add_metadata_to_storage, generate_metadata

if TYPE_CHECKING:
    from fragua.environments.environment import Environment

logger = get_logger(__name__)


class Agent(ABC, Generic[ParamsT]):
    """Agent class for ETL agents using shared Environment registries with pipeline helpers."""

    def __init__(self, name: str, environment: Environment) -> None:
        self.name: str = name
        self.environment: Environment = environment
        self.role: str
        self.action: str
        self.storage_type: str
        self._operations: list[dict[str, Any]] = []
        self._undo_stack: list[dict[str, Any]] = []

    # ----------------- Agent Summary ----------------- #
    def summary(self) -> Dict[str, object]:
        """
        Return a JSON-serializable summary of the agent state.
        """

        # ---- Environment info ----
        env_name = getattr(self.environment, "name", None)
        manager = getattr(self.environment, "manager", None)
        manager = manager() if callable(manager) else None

        # ---- Operations (convert timestamps only) ----
        ops_serialized: list[Dict[str, object]] = []
        for op in self._operations:
            ts = op.get("timestamp")
            ops_serialized.append(
                {
                    "action": op.get("action"),
                    "style": op.get("style_name") or op.get("style"),
                    "timestamp": ts.isoformat() if ts is not None else None,
                }
            )

        # ---- Undo stack (no params) ----
        undo_serialized: list[Dict[str, object]] = []
        for item in self._undo_stack:
            undo_serialized.append(
                {
                    "operation": item.get("operation"),
                    "style": item.get("style"),
                }
            )

        return {
            "agent_name": self.name,
            "role": getattr(self, "role", None),
            "action": getattr(self, "action", None),
            "storage_type": getattr(self, "storage_type", None),
            "environment_name": env_name,
            "operation_count": len(self._operations),
            "operations": ops_serialized,
            "undo_stack_size": len(self._undo_stack),
            "undo_stack": undo_serialized,
        }

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
    def warehouse_manager(self) -> WarehouseManager:
        """Access the shared warehouse manager from the environment."""
        return self.environment.manager()

    # ----------------- Helpers ----------------- #
    def _determine_origin_name(self, origin: Any) -> Optional[str]:
        """Determine a string name for the origin of data for metadata."""
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
        """Attach metadata to a storage object."""
        origin_name = self._determine_origin_name(origin)
        metadata = generate_metadata(
            storage=storage,
            metadata_type="operation",
            origin_name=origin_name,
            style_name=style_name,
        )
        add_metadata_to_storage(storage, metadata)

    # ----------------- Operations Logging ----------------- #
    def _add_operation(self, style: str, params_instance: Params) -> None:
        self._operations.append(
            {
                "action": self.action,
                "style_name": style,
                "timestamp": datetime.now(timezone.utc),
                "params": params_instance,
            }
        )
        # Optional: backup for undo
        self._undo_stack.append(
            {"operation": "workflow", "style": style, "params": params_instance}
        )

    def get_operations(self) -> pd.DataFrame:
        """Return a DataFrame with all recorded operations done by the agent."""
        return pd.DataFrame(self._operations)

    def undo_last_operation(self) -> bool:
        """Undo the last workflow operation."""
        if not self._undo_stack:
            return False
        last = self._undo_stack.pop()
        # Here you could implement logic to reverse the effects
        self._operations = [op for op in self._operations if op != last.get("params")]
        logger.info("Undid last operation: %s", last.get("style"))
        return True

    # ----------------- Storage Management ----------------- #
    def create_storage(self, data: Any) -> Storage[Any]:
        """Create a storage type for a given data."""
        storage_cls = STORAGE_CLASSES.get(self.storage_type)
        if not storage_cls:
            raise TypeError(f"Invalid storage type: '{self.storage_type}'.")
        return (
            storage_cls(data=data)
            if self.storage_type != "Container"
            else storage_cls()
        )

    def add_to_warehouse(
        self, storage: Storage[Box], storage_name: str | None = None
    ) -> None:
        """Pipeline for adding an object to warehouse with logging."""
        name = storage_name or getattr(storage, "name", None)
        self.warehouse_manager.add(
            storage=storage, storage_name=name, agent_name=self.name
        )

    def get_from_warehouse(self, storage_name: str) -> Box:
        """Pipeline for retrieving a storage object from warehouse with type checking."""
        storage = self.warehouse_manager.get(
            storage_name=storage_name, agent_name=self.name
        )
        if storage is None:
            raise TypeError("Storage not found in warehouse.")
        if not isinstance(storage, Box):
            raise TypeError("Storage is not a Box.")
        return storage

    def auto_store(
        self, style: str, storage: Storage[Box], save_as: str | None = None
    ) -> None:
        """Add a storage object automatically using pipeline helpers."""
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
        """Common workflow pipeline for agents."""
        style = style.lower()
        params_instance = params or self.get_registred_class(
            "params", style, self.action
        )(**kwargs)
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
        """Execute the agent's task."""
        self._execute_workflow(style, save_as, params, **kwargs)
