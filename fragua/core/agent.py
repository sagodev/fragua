"""
Agent class in Fragua.
Agents can take a role to work like a Miner, Blacksmith, or Transporter.
"""

from __future__ import annotations
from abc import abstractmethod
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
)
from datetime import datetime, timezone
import pandas as pd

from fragua.core.component import FraguaComponent
from fragua.core.storage import Storage, Box, STORAGE_CLASSES

from fragua.utils.logger import get_logger
from fragua.utils.metrics import add_metadata_to_storage, generate_metadata
from fragua.utils.security.security_context import FraguaToken
from fragua.utils.types.enums import (
    ActionType,
    AttrType,
    ComponentType,
    FieldType,
    MetadataType,
    StorageType,
)

if TYPE_CHECKING:
    from fragua.core.environment import FraguaEnvironment

logger = get_logger(__name__)

# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments


class FraguaAgent(FraguaComponent):
    """
    Base class for ETL agents operating within a shared Fragua Environment.

    A FraguaAgent encapsulates the execution logic of a single ETL role
    (extract, transform, or load) and provides a standardized workflow
    including function execution, storage handling, metadata generation,
    operation logging, undo support, and warehouse persistence.
    """

    def __init__(self, agent_name: str, environment: FraguaEnvironment) -> None:
        """
        Initialize the agent with a name and an execution environment.

        Args:
            agent_name: Unique identifier for the agent.
            environment: Shared Environment instance providing registries,
                warehouse manager, and configuration.
        """
        super().__init__(instance_name=agent_name)
        self.environment: FraguaEnvironment = environment
        self.token: FraguaToken
        self.action: ActionType
        self.storage_type: StorageType
        self._operations: List[Dict[str, Any]] = []
        self._undo_stack: List[Dict[str, Any]] = []

    # ----------------- Helpers ----------------- #
    def _require_token(self) -> FraguaToken:
        if self.token is None:
            raise RuntimeError(
                f"Security token not initialized for agent '{self.name}'."
            )
        return self.token

    def _determine_origin_name(self, origin: Any) -> Optional[str]:
        origin_name = None
        match origin:
            case Storage():
                origin_name = origin.__class__.__name__
            case str() | Path():
                origin_name = Path(origin).name
            case _:
                if hasattr(origin, FieldType.PATH.value) and isinstance(
                    origin.path, (str, Path)
                ):
                    origin_name = Path(origin.path).name
                elif hasattr(origin, FieldType.DATA.value) and isinstance(
                    origin.data, pd.DataFrame
                ):
                    origin_name = "DataFrame"
        return origin_name

    def _generate_storage_name(self, storage_name: str) -> str:
        return f"{storage_name}_{self.action}_data"

    def _resolve_function(self, function_key: str) -> Callable[..., Any]:
        func_spec = self.environment.get(
            self.action,
            ComponentType.FUNCTION,
            function_key,
        )

        if func_spec is None:
            raise ValueError(
                f"Function '{function_key}' not registered for action '{self.action}'."
            )

        func = func_spec[ComponentType.FUNCTION.value]

        # ----------------- EXTRACT ----------------- #
        if self.action == ActionType.EXTRACT.value:

            def _extract_executor(**kwargs: Any) -> pd.DataFrame:
                result = func(**kwargs)

                if not isinstance(result, pd.DataFrame):
                    raise TypeError("EXTRACT functions must return a pandas DataFrame")

                return result

            return _extract_executor

        # ----------------- TRANSFORM ----------------- #
        if self.action == ActionType.TRANSFORM.value:

            def _transform_executor(
                *,
                input_data: pd.DataFrame,
                **kwargs: Any,
            ) -> pd.DataFrame:
                result = func(input_data=input_data, **kwargs)

                if not isinstance(result, pd.DataFrame):
                    raise TypeError(
                        "TRANSFORM functions must return a pandas DataFrame"
                    )

                return result

            return _transform_executor

        # ----------------- LOAD ----------------- #
        if self.action == ActionType.LOAD.value:

            def _load_executor(
                *,
                input_data: pd.DataFrame,
                **kwargs: Any,
            ) -> Any:
                return func(input_data=input_data, **kwargs)

            return _load_executor

        raise RuntimeError(f"Unsupported agent action: {self.action}")

    def _normalize_input_data(self, input_data: Any) -> pd.DataFrame:
        if input_data is None:
            return pd.DataFrame()

        if isinstance(input_data, pd.DataFrame):
            return input_data

        if isinstance(input_data, list):
            return pd.DataFrame(input_data)

        if isinstance(input_data, dict):
            if any(isinstance(v, (list, tuple)) for v in input_data.values()):
                return pd.DataFrame(input_data)

            return pd.DataFrame([input_data])

        raise TypeError(f"Unsupported input_data type: {type(input_data).__name__}")

    # ----------------- Metadata ----------------- #
    def _generate_operation_metadata(
        self, target_name: str, storage: Storage[Any]
    ) -> None:
        metadata = generate_metadata(
            storage=storage,
            metadata_type=MetadataType.OPERATION.value,
            target_name=target_name,
        )
        add_metadata_to_storage(storage, metadata)

    # ----------------- Operations Logging ----------------- #
    def _add_operation(self, function_key: str) -> None:

        func_spec = self.environment.get(
            self.action, ComponentType.FUNCTION, function_key
        )

        if func_spec is None:
            raise ValueError(
                f"Function '{function_key}' not registered for action '{self.action}'."
            )

        func_name = getattr(
            func_spec.get(ComponentType.FUNCTION.value), "__name__", str(func_spec)
        )

        self._operations.append(
            {
                FieldType.ACTION.value: self.action.value,
                ComponentType.FUNCTION.value: func_name,
                MetadataType.TIMESTAMP.value: datetime.now(timezone.utc),
            }
        )
        self._undo_stack.append(
            {
                MetadataType.OPERATION.value: "workflow",
                ComponentType.FUNCTION.value: func_name,
            }
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
        function_key = last.get(ComponentType.FUNCTION.value)

        self._operations = [
            op
            for op in self._operations
            if op.get(ComponentType.FUNCTION.value) != function_key
        ]

        logger.info("Undid last operation: %s", function_key)
        return True

    # ----------------- Storage Management ----------------- #
    def create_storage(
        self,
        *,
        data: Any,
        function_name: str,
        storage_name: str | None = None,
    ) -> Storage[Any]:
        """
        Instantiate a storage object based on the agent storage type.

        Args:
            data:
                Data to be wrapped by the storage.
            target_name:
                Executed target identifier.
            storage_name:
                Optional explicit storage name. If not provided, a default
                name is generated automatically.

        Returns:
            A Storage instance.

        Raises:
            TypeError:
                If the storage type is invalid.
        """
        storage_cls = STORAGE_CLASSES.get(self.storage_type)
        if not storage_cls:
            raise TypeError(f"Invalid storage type: '{self.storage_type}'.")

        name = (
            storage_name if storage_name else self._generate_storage_name(function_name)
        )

        if self.storage_type != StorageType.CONTAINER.value:
            return storage_cls(name, data)

        return storage_cls(name)

    def add_to_warehouse(
        self,
        storage: Storage[Box],
        storage_name: str | None = None,
        *,
        overwrite: bool = False,
    ) -> bool:
        """
        Persist a storage object into the warehouse.
        """
        name = storage_name or getattr(storage, AttrType.NAME.value, None)
        if not name:
            raise ValueError("Storage name could not be resolved.")

        warehouse = self.environment.warehouse

        return warehouse.add_storage(
            name=name,
            storage=storage,
            token=self._require_token(),
            agent_name=self.name,
            overwrite=overwrite,
        )

    def get_from_warehouse(self, storage_name: str) -> Box:
        """
        Retrieve a Box storage from the warehouse.
        """
        warehouse = self.environment.warehouse

        storage = warehouse.get_storages(
            token=self.token,
            storage_name=storage_name,
            agent_name=self.name,
        )

        if storage is None:
            raise TypeError("Storage not found in warehouse.")
        if not isinstance(storage, Box):
            raise TypeError("Storage is not a Box.")

        return storage

    def auto_store(self, storage: Storage[Box]) -> None:
        """
        Persist a storage object using its own name.
        """
        self.add_to_warehouse(storage)

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
        env_name = getattr(self.environment, AttrType.NAME.value, None)

        ops_serialized: list[Dict[str, object]] = []
        for op in self._operations:
            ts = op.get(MetadataType.TIMESTAMP.value)
            ops_serialized.append(
                {
                    FieldType.ACTION.value: op.get(FieldType.ACTION.value),
                    ComponentType.FUNCTION.value: op.get(ComponentType.FUNCTION.value),
                    MetadataType.TIMESTAMP.value: ts.isoformat() if ts else None,
                }
            )

        undo_serialized: list[Dict[str, object]] = []
        for item in self._undo_stack:
            undo_serialized.append(
                {
                    MetadataType.OPERATION.value: item.get(
                        MetadataType.OPERATION.value
                    ),
                    ComponentType.FUNCTION.value: item.get(
                        ComponentType.FUNCTION.value
                    ),
                }
            )

        return {
            ComponentType.AGENT.value: self.name,
            MetadataType.TOKEN_ID.value: self.token.token_id,
            FieldType.ACTION.value: self.action.value,
            FieldType.STORAGE_TYPE.value: self.storage_type.value,
            ComponentType.ENVIRONMENT.value: env_name,
            MetadataType.OPERATIONS_COUNT.value: len(self._operations),
            MetadataType.OPERATIONS_DONE.value: ops_serialized,
            "undo_stack_size": len(self._undo_stack),
            "undo_stack": undo_serialized,
        }

    # ----------------- Work Pipeline ----------------- #
    def _execute_workflow(
        self,
        target_type: str,
        *,
        input_data: pd.DataFrame | None = None,
        save_as: str | None = None,
        **kwargs: Any,
    ) -> None:

        func = self._resolve_function(target_type)

        data = self._normalize_input_data(input_data)

        if self.action == ActionType.EXTRACT:
            result = func(**kwargs)
        else:
            result = func(input_data=data, **kwargs)

        storage = self.create_storage(
            data=result,
            function_name=target_type,
            storage_name=save_as,
        )

        self._generate_operation_metadata(target_type, storage)
        self._add_operation(target_type)

        self.auto_store(storage)

    # ----------------- Work method ----------------- #
    @abstractmethod
    def work(
        self,
        target_type: str,
        apply_to: str | list[str] | None = None,
        save_as: str | None = None,
        input_data: pd.DataFrame | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Execute the agent-specific task.
        Args:
            target_type: Function identifier to execute (e.g. "csv", "excel", etc).
            apply_to: Optional storage name(s) or input reference.
            save_as: Optional explicit name for persisted storage.
            input_data: Optional input DataFrame for transform/load.
            **kwargs: Additional parameters.
        """
        if input_data is None and apply_to is not None:
            if isinstance(apply_to, list):
                input_data = pd.concat(
                    [self.get_from_warehouse(name).data for name in apply_to]
                )
            else:
                input_data = self.get_from_warehouse(apply_to).data

        self._execute_workflow(
            target_type=target_type,
            input_data=input_data,
            save_as=save_as,
            **kwargs,
        )
