"""
Base class for all ETL agents in Fragua.

Defines the common interface and shared behavior for
agents like Miner, Blacksmith, and Transporter.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import (
    Any,
    Dict,
    Type,
    TypeVar,
    Generic,
    TYPE_CHECKING,
    Optional,
    Literal,
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
from fragua.utils.metrics import calculate_checksum

if TYPE_CHECKING:
    from fragua.agents.storage_manager import StorageManager

# Generic type variables
StyleT = TypeVar("StyleT", bound=BaseStyle[Any, Any])
ResultT = TypeVar("ResultT")

logger = get_logger("BaseAgent")


class BaseAgent(ABC, Generic[StyleT, ResultT]):
    """Abstract base class for ETL agents with built-in support
    for learning and applying registered styles."""

    style_registry: Dict[str, Type[StyleT]] = {}
    result_type: Optional[Type[ResultT]] = None

    def __init__(self, name: str):
        self.name: str = name
        self.known_styles: Dict[str, StyleT] = {}
        self.learned_styles: Dict[str, dict[Any, Any]] = {}
        self._operations_rows: list[dict[Any, Any]] = []

    def _wrap_storage(
        self,
        result: Any,
        name_prefix: str = "result",
        operation_metadata: Optional[dict[str, Any]] = None,
    ) -> ResultT:
        """
        Convert raw style output into the appropriate storage object.
        Attach operation metadata automatically.

        Args:
            result: Raw output from style (DataFrame or list).
            name_prefix: Prefix for the storage object name.
            operation_metadata: Optional metadata dictionary to attach.

        Returns:
            ResultT: Storage object (Wagon, Box, Container) with metadata attached.
        """
        if self.result_type is None:
            raise TypeError(
                f"Cannot wrap result: {self.__class__.__name__} has no result_type defined."
            )

        type_name = self.result_type.__name__.lower()
        storage_name = f"{name_prefix}_{self.name}"

        if type_name == "wagon":
            storage_obj = Wagon(data=result, name=storage_name)
        elif type_name == "box":
            storage_obj = Box(data=result, name=storage_name)
        elif type_name == "container":
            storage_obj = Container(data=result, name=storage_name)
        else:
            raise TypeError(
                f"Result type '{self.result_type.__name__}' is not a valid storage type"
            )

        # Attach metadata if provided
        if operation_metadata is not None:
            storage_obj.attach_metadata(operation_metadata)

        return cast(ResultT, storage_obj)

    def _normalize_input(self, input_data: Any) -> Any:
        """
        Convert input data into a format compatible with MineStyle.
        Accepts BaseStorage, DataFrame, or any BaseParams object.
        """
        if isinstance(input_data, BaseStorage):
            if input_data.data is None:
                raise ValueError(f"{input_data.name} has no data to process")
            return input_data.data
        if isinstance(input_data, pd.DataFrame):
            return input_data
        if isinstance(input_data, BaseParams):
            return input_data

        raise TypeError(
            f"{self.__class__.__name__} cannot process input of type {type(input_data)}"
        )

    def record_operation(
        self,
        style_name: str,
        result_obj: BaseStorage[Any],
    ) -> dict[str, Any]:
        """
        Record an operation in the internal metadata and return the metadata dictionary.
        Includes checksum, local time, and timezone offset.

        Args:
            style_name: Name of the style applied.
            result_obj: Output object of the style (Wagon/Box/Container).

        Returns:
            dict: Metadata dictionary for this operation.
        """
        result_name = getattr(result_obj, "name", None)
        result_data = getattr(result_obj, "data", None)
        result_shape = getattr(result_data, "shape", (None, None))

        # Use global calculate_checksum function to ensure deterministic checksum
        style_checksum = calculate_checksum(result_data)

        # Local time and timezone
        now_utc = datetime.now(timezone.utc)
        local_tz = datetime.now().astimezone().tzinfo
        now_local = now_utc.astimezone(local_tz)

        local_time_str = now_local.strftime("%H:%M:%S.%f")[:-3]
        timezone_offset = now_local.strftime("%z")
        timezone_offset = (
            timezone_offset[:3] + ":" + timezone_offset[3:]
            if len(timezone_offset) == 5
            else timezone_offset
        )

        operation_meta: dict[str, Any] = {
            "local_time": local_time_str,
            "timezone_offset": timezone_offset,
            "ouput_name": result_name,
            "rows": result_shape[0],
            "columns": result_shape[1],
            "style_name": style_name,
            "checksum": style_checksum,
        }

        # Attach metadata to storage
        result_obj.attach_metadata(operation_meta)

        # Record internally
        self._operations_rows.append(operation_meta)

        return operation_meta

    def get_operations(self) -> pd.DataFrame:
        """Return a DataFrame with all recorded operations."""
        return pd.DataFrame(self._operations_rows)

    # ---------------- Learning ---------------- #
    def learn_style(self, style_instance: StyleT) -> None:
        """Register a style instance with this agent."""
        self.known_styles[style_instance.style_name] = style_instance
        self.learned_styles[style_instance.style_name] = {
            "class": style_instance.__class__.__name__,
            "learned_at": datetime.now(timezone.utc),
        }
        logger.info("[%s] Learned style '%s'", self.name, style_instance.style_name)

    def learn_style_by_name(self, name: str) -> None:
        """
        Create and learn a style dynamically from the registry.
        The style is registered with the same name used to look it up.

        Args:
            name: Name of the style to create and register

        Raises:
            ValueError: If style name is not in registry
        """
        if name not in self.style_registry:
            raise ValueError(f"No style registered under name '{name}'")
        style_cls = self.style_registry[name]
        instance = style_cls(style_name=name)
        self.learn_style(instance)

    # ---------------- Apply Style ---------------- #
    def apply_style(self, style_name: str, data: Any) -> ResultT:
        """
        Apply a learned style, wrap the result in a storage object,
        and attach metadata automatically.

        Args:
            style_name: Name of the style to apply.
            data: Input data for the style (DataFrame or BaseStorage).

        Returns:
            ResultT: Wrapped storage object with metadata.
        """
        if style_name not in self.known_styles:
            raise ValueError(f"Style '{style_name}' not learned")

        style = self.known_styles[style_name]
        normalized_data = self._normalize_input(data)
        raw_result = style.use(normalized_data)

        # 1. Wrap in Storage first
        result_storage = self._wrap_storage(raw_result, name_prefix=style_name)

        # 2. Record operation using the Storage (checksum will match Storage)
        operation_metadata = self.record_operation(style_name, result_storage)

        # 3. Attach the operation metadata to the storage object
        result_storage.attach_metadata(operation_metadata)

        logger.info("[%s] Applied style '%s'", self.name, style_name)
        return result_storage

    # ---------------- Storage Interaction ---------------- #
    def store_result(
        self, storage_manager: "StorageManager", result: ResultT, name: str
    ) -> None:
        """
        Store a result object in the StorageManager using the appropriate save method.

        Args:
            storage_manager: The StorageManager instance to store the result in
            result: The result object to store (must match ResultT type)
            name: Name to store the result under

        Raises:
            AttributeError: If StorageManager doesn't implement required save method
            TypeError: If result_type is not defined for this agent
            ValueError: If the result type does not map to a valid storage type
        """
        if self.result_type is None:
            raise TypeError(
                f"Cannot store result: {self.__class__.__name__} has no result_type defined."
            )

        obj_type_str = self.result_type.__name__.lower()
        if obj_type_str not in ["wagon", "box", "container"]:
            raise ValueError(
                f"Result type '{self.result_type.__name__}' is not a valid storage type"
            )

        ObjectType = Literal["wagon", "box", "container"]
        obj_type: ObjectType = cast(ObjectType, obj_type_str)

        try:
            storage_manager.save(obj_type, name, result)
        except AttributeError as exc:
            raise AttributeError(
                "StorageManager does not implement 'save(obj_type, name, obj)'"
            ) from exc

        logger.info(
            "[%s] Stored %s '%s' in StorageManager",
            self.name,
            self.result_type.__name__,
            name,
        )

    # ---------------- Abstract Work ---------------- #
    @abstractmethod
    def work(self, *args: Any, **kwargs: Any) -> ResultT:
        """
        Abstract method that defines how the agent performs its task.
        Should typically call apply_style().

        Args:
            *args: Variable positional arguments
            **kwargs: Variable keyword arguments

        Returns:
            ResultT: The result type specific to this agent subclass
        """

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
