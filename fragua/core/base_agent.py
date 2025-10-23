"""
Base class for all ETL agents in Fragua.

Defines the common interface and shared behavior for
agents like Miner, Blacksmith, and Transporter.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
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

    # ----------------- Helpers ----------------- #
    def _get_local_time_and_offset(self) -> tuple[str, str]:
        """Return local time string and timezone offset."""
        now_utc = datetime.now(timezone.utc)
        local_tz = datetime.now().astimezone().tzinfo
        now_local = now_utc.astimezone(local_tz)
        local_time_str = now_local.strftime("%H:%M:%S.%f")[:-3]
        timezone_offset = now_local.strftime("%z")
        if len(timezone_offset) == 5:
            timezone_offset = timezone_offset[:3] + ":" + timezone_offset[3:]
        return local_time_str, timezone_offset

    def _determine_input_name(self, input_obj: Any) -> str | None:
        """Extract a meaningful input name for the operation metadata."""
        # If BaseStorage (Wagon, Box, Container)
        if isinstance(input_obj, BaseStorage):
            return input_obj.name

        # If string or Path (file)
        if isinstance(input_obj, (str, Path)):
            return Path(input_obj).name

        # If params with a path attribute
        if hasattr(input_obj, "path") and isinstance(input_obj.path, (str, Path)):
            return Path(input_obj.path).name

        # If params with a data attribute that is BaseStorage
        if hasattr(input_obj, "data") and isinstance(input_obj.data, BaseStorage):
            return input_obj.data.name

        # If params with a data attribute that is DataFrame, return generic name
        if hasattr(input_obj, "data") and isinstance(input_obj.data, pd.DataFrame):
            return "data"

        # If object has 'name'
        if hasattr(input_obj, "name"):
            return str(input_obj.name)

        return None

    def _determine_output_type(self, output_obj: Any) -> str | None:
        """Extract a meaningful output type for the operation metadata."""
        if isinstance(output_obj, Wagon):
            return "wagon"
        if isinstance(output_obj, Box):
            return "box"
        if isinstance(output_obj, Container):
            return "container"

        return None

    def _generate_operation_metadata(
        self, style_name: str, output_obj: BaseStorage[Any], input_obj: Any
    ) -> dict[str, Any]:
        """
        Generate a metadata dictionary for an operation.

        Args:
            style_name: Name of the style applied.
            result_obj: Wrapped storage object (Wagon/Box/Container).
            input_data: Original input to the style.

        Returns:
            dict: Metadata dictionary.
        """
        # Determine input name
        input_name = self._determine_input_name(input_obj)

        # Determine storage type
        output_type = self._determine_output_type(output_obj)

        # Extract rows and columns
        rows, columns = getattr(output_obj.data, "shape", (None, None))

        # Checksum from storage
        checksum = output_obj.checksum

        # Local time and timezone
        local_time_str, timezone_offset = self._get_local_time_and_offset()

        return {
            "input_name": input_name,
            "style_name": style_name,
            "local_time": local_time_str,
            "timezone_offset": timezone_offset,
            "output_name": output_obj.name,
            "output_type": output_type,
            "rows": rows,
            "columns": columns,
            "checksum": checksum,
        }

    # ----------------- Operations ----------------- #
    def record_operation(
        self, style_name: str, result_obj: Any, input_data: Any = None
    ) -> dict[str, Any]:
        """Record an operation and return its metadata."""
        metadata = self._generate_operation_metadata(style_name, result_obj, input_data)
        self._operations_rows.append(metadata)
        return metadata

    def get_operations(self) -> pd.DataFrame:
        """Return a DataFrame with all recorded operations."""
        return pd.DataFrame(self._operations_rows)

    # ----------------- Learning ----------------- #
    def learn_style(self, style_instance: StyleT) -> None:
        """Register a style instance with this agent."""
        self.known_styles[style_instance.style_name] = style_instance
        self.learned_styles[style_instance.style_name] = {
            "class": style_instance.__class__.__name__,
            "learned_at": datetime.now(timezone.utc),
        }
        logger.info("[%s] Learned style '%s'", self.name, style_instance.style_name)

    def learn_style_by_name(self, name: str) -> None:
        """Create and learn a style dynamically from the registry."""
        if name not in self.style_registry:
            raise ValueError(f"No style registered under name '{name}'")
        style_cls = self.style_registry[name]
        instance = style_cls(style_name=name)
        self.learn_style(instance)

    # ----------------- Apply Style ----------------- #
    def _wrap_storage(
        self, result: Any, operation_metadata: Optional[dict[str, Any]] = None
    ) -> ResultT:
        """Convert raw style output into the appropriate storage object and attach metadata."""
        if self.result_type is None:
            raise TypeError(
                f"Cannot wrap result: {self.__class__.__name__} has no result_type defined."
            )

        type_name = self.result_type.__name__.lower()
        storage_obj: BaseStorage[Any] = None

        if type_name == "wagon":
            storage_obj = Wagon(data=result, name=f"wagon_{self.name}")
        elif type_name == "box":
            storage_obj = Box(data=result, name=f"box_{self.name}")
        elif type_name == "container":
            storage_obj = Container(data=result, name=f"container_{self.name}")
        else:
            raise TypeError(
                f"Result type '{self.result_type.__name__}' is not a valid storage type"
            )

        if operation_metadata is not None:
            storage_obj.attach_metadata(operation_metadata)

        return cast(ResultT, storage_obj)

    def _normalize_input(self, input_data: Any) -> Any:
        """Convert input data into a format compatible with MineStyle."""
        if isinstance(input_data, BaseStorage):
            if input_data.data is None:
                raise ValueError(f"{input_data.name} has no data to process")
            return input_data.data
        if isinstance(input_data, pd.DataFrame):
            return input_data
        if isinstance(input_data, BaseParams):
            return input_data
        return input_data

    def apply_style(self, style_name: str, data: Any) -> ResultT:
        """
        Apply a learned style, wrap the result in a storage object,
        attach operation metadata including input name, type, rows, columns, checksum.

        Args:
            style_name: Name of the style to apply.
            data: Input data for the style (DataFrame, BaseStorage, or BaseParams).

        Returns:
            ResultT: Wrapped storage object with metadata.
        """
        if style_name not in self.known_styles:
            raise ValueError(f"Style '{style_name}' not learned")

        original_input = data

        style = self.known_styles[style_name]
        normalized_data = self._normalize_input(data)

        # Apply the style
        raw_result = style.use(normalized_data)

        # Wrap result in storage
        wrapped_result = self._wrap_storage(raw_result)

        # Generate operation metadata
        operation_metadata = self._generate_operation_metadata(
            style_name=style_name, output_obj=wrapped_result, input_obj=original_input
        )

        # Attach metadata to the storage
        wrapped_result.attach_metadata(operation_metadata)

        # Record internally in the agent
        self._operations_rows.append(operation_metadata)

        logger.info("[%s] Applied style '%s'", self.name, style_name)
        return wrapped_result

    # ----------------- Storage Interaction ----------------- #
    def store_result(
        self, storage_manager: "StorageManager", result: ResultT, name: str
    ) -> None:
        """Store a result object in the StorageManager."""
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

    # ----------------- Abstract Work ----------------- #
    @abstractmethod
    def work(self, *args: Any, **kwargs: Any) -> ResultT:
        """Abstract method that defines how the agent performs its task."""
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
