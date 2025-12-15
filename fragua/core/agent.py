"""
Agent class in Fragua.
Agents can take a role to work like a Miner, Blacksmith, or Transporter.
"""

from __future__ import annotations
from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Generic, List, Optional, Type, cast
from datetime import datetime, timezone

import pandas as pd

from fragua.core.component import FraguaComponent
from fragua.core.params import FraguaParams, FraguaParamsT
from fragua.core.storage import Storage, Box, STORAGE_CLASSES

from fragua.core.style import FraguaStyle
from fragua.utils.logger import get_logger
from fragua.utils.metrics import add_metadata_to_storage, generate_metadata

if TYPE_CHECKING:
    from fragua.core.environment import FraguaEnvironment

logger = get_logger(__name__)


class FraguaAgent(FraguaComponent, Generic[FraguaParamsT]):
    """
    Base class for ETL agents operating within a shared Fragua Environment.

    A FraguaAgent encapsulates the execution logic of a single ETL role
    (extract, transform, or load) and provides a standardized workflow
    including parameter resolution, style execution, storage handling,
    metadata generation, operation logging, undo support, and warehouse
    persistence.

    The agent relies on Environment registries to dynamically resolve
    styles, parameters, and storage implementations.
    """

    def __init__(self, agent_name: str, environment: FraguaEnvironment) -> None:
        """
        Initialize the agent with a name and an execution environment.

        Args:
            agent_name: Unique identifier for the agent.
            environment: Shared Environment instance providing registries,
                warehouse manager, and configuration.
        """
        super().__init__(component_name=agent_name)
        self.environment: FraguaEnvironment = environment
        self.role: str
        self.action: str
        self.storage_type: str
        self._operations: List[Dict[str, Any]] = []
        self._undo_stack: List[Dict[str, Any]] = []

    # ----------------- Agent Summary ----------------- #
    def summary(self) -> Dict[str, object]:
        """
        Generate a structured summary of the agent state and execution history.

        The summary includes agent metadata, environment context, a serialized
        view of executed operations, and the current undo stack state.

        Returns:
            A dictionary containing agent identification, configuration,
            execution metrics, operation history, and undo information.
        """

        env_name = getattr(self.environment, "name", None)
        manager = getattr(self.environment, "manager", None)
        manager = manager() if callable(manager) else None

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

    # ----------------- Helpers ----------------- #
    def _determine_origin_name(self, origin: Any) -> Optional[str]:
        """
        Infer a human-readable origin name for metadata generation.

        The origin may represent a storage object, file path, DataFrame,
        or any object exposing a `path` or `data` attribute.

        Args:
            origin: Source object used to infer origin metadata.

        Returns:
            A string representing the origin name, or None if it cannot
            be determined.
        """
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
        """
        Generate a default storage name based on style and agent action.

        Args:
            style_name: Executed style identifier.

        Returns:
            A standardized storage name string.
        """
        return f"{style_name}_{self.action}_data"

    def _instantiate_params(
        self,
        style: str,
        params: Optional[FraguaParams],
        **kwargs: Any,
    ) -> FraguaParams:
        """
        Resolve and instantiate parameter objects for a given style.

        If an explicit Params instance is provided, it is returned unchanged.
        Otherwise, the Params class is resolved from the Environment registry
        and instantiated using the supplied keyword arguments.

        Args:
            style: Style identifier used to resolve the Params class.
            params: Optional pre-instantiated Params object.
            **kwargs: Keyword arguments for Params construction.

        Returns:
            An instantiated Params object.

        Raises:
            ValueError: If no Params class is registered for the given style.
        """
        if params is not None:
            return params

        params_cls = cast(
            Type[FraguaParams], self.environment.get_param(self.action, style)
        )
        if params_cls is None:
            raise ValueError(f"Params not found for style '{style}'.")

        return params_cls(**kwargs)

    def _instantiate_style(self, style: str) -> FraguaStyle[FraguaParams]:
        """
        Resolve and instantiate a style implementation for the agent action.

        Args:
            style: Style identifier to resolve.

        Returns:
            An instantiated FraguaStyle object.

        Raises:
            ValueError: If the style class cannot be resolved.
        """
        style_cls = cast(
            Type[FraguaStyle[FraguaParams]],
            self.environment.get_style(self.action, style),
        )
        if style_cls is None:
            raise ValueError(f"Style not found: '{style}'.")

        return style_cls()

    # ----------------- Metadata ----------------- #
    def _generate_operation_metadata(
        self, style_name: str, storage: Storage[Any], origin: Any
    ) -> None:
        """
        Generate and attach operation metadata to a storage object.

        Metadata captures contextual information such as origin, style,
        and operation type to support traceability and auditing.

        Args:
            style_name: Executed style identifier.
            storage: Storage instance receiving the metadata.
            origin: Source object used to infer origin metadata.
        """
        origin_name = self._determine_origin_name(origin)
        metadata = generate_metadata(
            storage=storage,
            metadata_type="operation",
            origin_name=origin_name,
            style_name=style_name,
        )
        add_metadata_to_storage(storage, metadata)

    # ----------------- Operations Logging ----------------- #
    def _add_operation(self, style: str, params_instance: FraguaParams) -> None:
        """
        Record an executed operation and register it for undo support.

        Args:
            style: Executed style identifier.
            params_instance: Parameters used during execution.
        """
        self._operations.append(
            {
                "action": self.action,
                "style_name": style,
                "timestamp": datetime.now(timezone.utc),
                "params": params_instance,
            }
        )
        self._undo_stack.append(
            {"operation": "workflow", "style": style, "params": params_instance}
        )

    def get_operations(self) -> pd.DataFrame:
        """
        Retrieve the execution history as a pandas DataFrame.

        Returns:
            A DataFrame containing all recorded operations.
        """
        return pd.DataFrame(self._operations)

    def undo_last_operation(self) -> bool:
        """
        Undo the most recent workflow operation.

        Returns:
            True if an operation was successfully undone, False if no
            operations were available.
        """
        if not self._undo_stack:
            return False

        last = self._undo_stack.pop()
        self._operations = [op for op in self._operations if op != last.get("params")]
        logger.info("Undid last operation: %s", last.get("style"))
        return True

    # ----------------- Storage Management ----------------- #
    def create_storage(self, data: Any) -> Storage[Any]:
        """
        Instantiate a storage object based on the agent storage type.

        Args:
            data: Data to be wrapped by the storage.

        Returns:
            A Storage instance.

        Raises:
            TypeError: If the storage type is invalid or not registered.
        """
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
        """
        Persist a storage object into the warehouse.

        Args:
            storage: Storage instance to persist.
            storage_name: Optional explicit name for the storage.

        Raises:
            RuntimeError: If the WarehouseManager is not initialized.
        """
        name = storage_name or getattr(storage, "name", None)
        manager = self.environment.manager
        if not manager:
            raise RuntimeError("WarehouseManager not initialized.")
        return manager.add(storage=storage, storage_name=name, agent_name=self.name)

    def get_from_warehouse(self, storage_name: str) -> Box:
        """
        Retrieve a storage object from the warehouse with type validation.

        Args:
            storage_name: Name of the storage to retrieve.

        Returns:
            A Box instance.

        Raises:
            RuntimeError: If the WarehouseManager is not initialized.
            TypeError: If the storage is missing or of an invalid type.
        """
        manager = self.environment.manager
        if not manager:
            raise RuntimeError("WarehouseManager not initialized.")

        storage = manager.get(storage_name=storage_name, agent_name=self.name)

        if storage is None:
            raise TypeError("Storage not found in warehouse.")
        if not isinstance(storage, Box):
            raise TypeError("Storage is not a Box.")
        return storage

    def auto_store(
        self, style: str, storage: Storage[Box], save_as: str | None = None
    ) -> None:
        """
        Automatically persist storage using a generated or provided name.

        Args:
            style: Executed style identifier.
            storage: Storage instance to persist.
            save_as: Optional explicit storage name.
        """
        name = save_as or self._generate_storage_name(style)
        self.add_to_warehouse(storage, name)

    # ----------------- Work Pipeline ----------------- #
    def _execute_workflow(
        self,
        style: str,
        save_as: Optional[str] = None,
        params: Optional[FraguaParamsT] = None,
        **kwargs: Any,
    ) -> None:
        """
        Execute the standardized agent workflow pipeline.

        This pipeline performs:
        - Parameter resolution
        - Style instantiation and execution
        - Storage creation
        - Metadata generation
        - Operation logging
        - Warehouse persistence

        Args:
            style: Style identifier to execute.
            save_as: Optional explicit name for persisted storage.
            params: Optional pre-instantiated Params object.
            **kwargs: Parameters forwarded to Params instantiation.
        """
        style = style.lower()

        params_instance = self._instantiate_params(style, params, **kwargs)
        style_instance = self._instantiate_style(style)

        stylized_data = style_instance.use(params_instance)
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
        params: Optional[FraguaParamsT] = None,
        **kwargs: Any,
    ) -> None:
        """
        Execute the agent-specific task.

        Concrete agents must implement this method to define how styles
        are applied and how the workflow is triggered.
        """
        self._execute_workflow(style, save_as, params, **kwargs)
