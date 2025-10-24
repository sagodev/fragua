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
    from fragua.agents.store_manager import StoreManager

# Generic type variables
StyleT = TypeVar("StyleT", bound=BaseStyle[Any, Any])
StorageT = TypeVar("StorageT", bound=BaseStorage[Any])

logger = get_logger("BaseAgent")


class BaseAgent(ABC, Generic[StyleT, StorageT]):
    """Abstract base class for ETL agents with built-in support
    for learning and applying registered styles."""

    style_registry: Dict[str, Type[StyleT]] = {}
    result_type: Optional[Type[StorageT]] = None

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
        """Extract a meaningful input name for the operation metadata with lazy logging."""
        result = None  # Store the determined name

        match input_obj:
            # Direct BaseStorage (Wagon, Box, Container)
            case BaseStorage():
                result = input_obj.name
                logger.debug("Detected BaseStorage input: %s", result)

            # Path or string path
            case str() | Path():
                result = Path(input_obj).name
                logger.debug("Detected file path input: %s", result)

            # Fallback cases
            case _:
                if hasattr(input_obj, "path") and isinstance(
                    input_obj.path, (str, Path)
                ):
                    result = Path(input_obj.path).name
                    logger.debug("Detected object with .path attribute: %s", result)
                elif hasattr(input_obj, "data") and isinstance(
                    input_obj.data, BaseStorage
                ):
                    result = input_obj.data.name
                    logger.debug(
                        "Detected object with .data as BaseStorage: %s", result
                    )
                elif hasattr(input_obj, "data") and isinstance(
                    input_obj.data, pd.DataFrame
                ):
                    result = "data"
                    logger.debug("Detected object with .data as DataFrame")
                elif hasattr(input_obj, "name"):
                    result = str(input_obj.name)
                    logger.debug("Detected object with .name attribute: %s", result)
                else:
                    logger.debug("Input type not recognized; returning None")

        return result

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
        """Generate a metadata dictionary for an operation."""
        input_name = self._determine_input_name(input_obj)
        output_type = self._determine_output_type(output_obj)
        rows, columns = getattr(output_obj.data, "shape", (None, None))
        checksum = output_obj.checksum
        local_time_str, timezone_offset = self._get_local_time_and_offset()

        metadata = {
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

        logger.debug("[%s] Generated operation metadata: %s", self.name, metadata)
        return metadata

    # ----------------- Operations ----------------- #
    def record_operation(
        self, style_name: str, result_obj: Any, input_data: Any = None
    ) -> dict[str, Any]:
        """Record an operation and return its metadata."""
        metadata = self._generate_operation_metadata(style_name, result_obj, input_data)
        self._operations_rows.append(metadata)
        logger.debug("[%s] Recorded operation for style '%s'", self.name, style_name)
        return metadata

    def get_operations(self) -> pd.DataFrame:
        """Return a DataFrame with all recorded operations."""
        logger.debug(
            "[%s] Returning %d recorded operations",
            self.name,
            len(self._operations_rows),
        )
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
    ) -> StorageT:
        """Convert raw style output into the appropriate storage object and attach metadata."""
        if self.result_type is None:
            raise TypeError(
                f"Cannot wrap result: {self.__class__.__name__} has no result_type defined."
            )

        type_name = self.result_type.__name__.lower()
        storage_obj: Optional[BaseStorage[Any]] = None

        match type_name:
            case "wagon":
                storage_obj = Wagon(data=result, name=f"wagon_{self.name}")
            case "box":
                storage_obj = Box(data=result, name=f"box_{self.name}")
            case "container":
                storage_obj = Container(data=result, name=f"container_{self.name}")
            case _:
                raise TypeError(
                    f"Result type '{self.result_type.__name__}' is not a valid storage type"
                )

        if operation_metadata is not None:
            storage_obj.attach_metadata(operation_metadata)
            logger.debug("[%s] Attached metadata to %s", self.name, storage_obj.name)

        return cast(StorageT, storage_obj)

    def _normalize_input(self, input_data: Any) -> Any:
        """Convert input data into a format compatible with MineStyle."""
        if isinstance(input_data, BaseStorage):
            if input_data.data is None:
                raise ValueError(f"{input_data.name} has no data to process")
            logger.debug("[%s] Normalized input from BaseStorage", self.name)
            return input_data.data
        if isinstance(input_data, pd.DataFrame):
            logger.debug("[%s] Normalized input as DataFrame", self.name)
            return input_data
        if isinstance(input_data, BaseParams):
            logger.debug("[%s] Normalized input as BaseParams", self.name)
            return input_data
        logger.debug("[%s] Input normalization returned original data", self.name)
        return input_data

    def apply_style(self, style_name: str, data: Any) -> StorageT:
        """Apply a learned style and record operation metadata."""
        if style_name not in self.known_styles:
            raise ValueError(f"Style '{style_name}' not learned")

        original_input = data
        style = self.known_styles[style_name]
        normalized_data = self._normalize_input(data)

        logger.debug(
            "[%s] Applying style '%s' with normalized input", self.name, style_name
        )
        raw_result = style.use(normalized_data)
        wrapped_result = self._wrap_storage(raw_result)

        operation_metadata = self._generate_operation_metadata(
            style_name=style_name, output_obj=wrapped_result, input_obj=original_input
        )
        wrapped_result.attach_metadata(operation_metadata)
        self._operations_rows.append(operation_metadata)

        logger.info("[%s] Applied style '%s'", self.name, style_name)
        return wrapped_result

    # ----------------- Storage Interaction ----------------- #
    def store_result(
        self, storage_manager: "StoreManager", result: StorageT, name: str
    ) -> None:
        """Store a result object in the StoreManager."""
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
            logger.info(
                "[%s] Stored %s '%s' in StoreManager",
                self.name,
                self.result_type.__name__,
                name,
            )
        except AttributeError as exc:
            raise AttributeError(
                "StoreManager does not implement 'save(obj_type, name, obj)'"
            ) from exc

    # ----------------- Abstract Work ----------------- #
    @abstractmethod
    def work(self, *args: Any, **kwargs: Any) -> StorageT:
        """Abstract method that defines how the agent performs its task."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
