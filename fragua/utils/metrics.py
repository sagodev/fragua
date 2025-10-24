"""
Metrics Utilities for Fragua ETL Framework.

This module provides stable and deterministic checksum calculations
for various data structures including pandas DataFrames, dictionaries,
lists, and other Python objects. It ensures reproducible checksums
by serializing the data in a consistent way.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, cast, Optional, Dict
import pandas as pd
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


def _serialize_dataframe(df: pd.DataFrame) -> bytes:
    """Make a copy and sort columns to guarantee deterministic ordering."""
    df_copy = df.copy()
    cols = sorted(df_copy.columns.tolist())
    df_copy = df_copy[cols]
    csv_str = cast(str, df_copy.to_csv(index=False))
    return csv_str.encode("utf-8")


def _serialize_other(obj: Any) -> bytes:
    """Serialize dictionaries, lists, or generic Python objects into bytes."""
    if isinstance(obj, (dict, list)):
        serialized = json.dumps(obj, sort_keys=True, default=str)
    else:
        serialized = repr(obj)
    return serialized.encode("utf-8")


def calculate_checksum(data: Any, algorithm: str = "sha256") -> str:
    """
    Calculate a stable checksum for DataFrame, dict, list or other objects.

    - DataFrame: sorted columns + to_csv(index=False)
    - dict/list: json.dumps(sort_keys=True)
    - others: str(obj)
    """
    if isinstance(data, pd.DataFrame):
        content = _serialize_dataframe(data)
    else:
        content = _serialize_other(data)

    h = hashlib.new(algorithm)
    h.update(content)
    return h.hexdigest()


def get_local_time_and_offset() -> tuple[str, str]:
    """Return local time string and timezone offset."""
    now_utc = datetime.now(timezone.utc)
    local_tz = datetime.now().astimezone().tzinfo
    now_local = now_utc.astimezone(local_tz)
    local_time_str = now_local.strftime("%H:%M:%S.%f")[:-3]
    timezone_offset = now_local.strftime("%z")
    if len(timezone_offset) == 5:
        timezone_offset = timezone_offset[:3] + ":" + timezone_offset[3:]
    return local_time_str, timezone_offset


def normalize_input(agent: Any, input_data: Any) -> Any:
    """
    Convert input data into a format compatible with BaseStyle.

    - If input is BaseStorage, return its `.data`.
    - If input is DataFrame or BaseParams, return as is.
    - Otherwise, return the original object.
    """
    from fragua.core.base_storage import BaseStorage
    from fragua.core.base_params import BaseParams

    if isinstance(input_data, BaseStorage):
        if input_data.data is None:
            raise ValueError(f"{input_data.name} has no data to process")
        agent_name = getattr(agent, "name", "unknown")
        logger.debug("[%s] Normalized input from BaseStorage", agent_name)
        return input_data.data

    if isinstance(input_data, pd.DataFrame):
        agent_name = getattr(agent, "name", "unknown")
        logger.debug("[%s] Input is already a DataFrame", agent_name)
        return input_data

    if isinstance(input_data, BaseParams):
        agent_name = getattr(agent, "name", "unknown")
        logger.debug("[%s] Input is BaseParams", agent_name)
        return input_data

    agent_name = getattr(agent, "name", "unknown")
    logger.debug("[%s] Input normalization returned original data", agent_name)
    return input_data


def generate_metadata(
    obj: Any,
    *,
    metadata_type: str,
    input_name: Optional[str] = None,
    style_name: Optional[str] = None,
    agent_name: Optional[str] = None,
    store_manager_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate metadata dictionary for objects with .data and .name.

    metadata_type: 'base', 'operation', or 'save'
    """
    data_attr = getattr(obj, "data", obj)
    rows, columns = getattr(data_attr, "shape", (None, None))
    checksum = calculate_checksum(data_attr)
    local_time, timezone_offset = get_local_time_and_offset()

    base_metadata: dict[str, Any] = {
        "local_time": local_time,
        "timezone_offset": timezone_offset,
        "rows": rows,
        "columns": columns,
        "checksum": checksum,
    }

    name_attr = getattr(obj, "name", None)
    class_type = obj.__class__.__name__.lower()

    if metadata_type == "base":
        base_metadata.update({"name": name_attr, "type": class_type})
    elif metadata_type == "operation":
        base_metadata.update(
            {
                "input_name": input_name,
                "style_name": style_name,
                "output_name": name_attr,
                "output_type": class_type,
                "operation_checksum": checksum,
            }
        )
    elif metadata_type == "save":
        base_metadata.update(
            {
                "store_manager": store_manager_name,
                "agent_name": agent_name,
                "save_checksum": checksum,
            }
        )
    else:
        raise ValueError(f"Unknown metadata_type '{metadata_type}'")

    return base_metadata


def add_metadata_to_storage(
    storage: Any,
    metadata: Optional[dict[str, object]] = None,
) -> None:
    """
    Add or merge metadata into a unified metadata dictionary of a storage object.

    Args:
        storage (BaseStorage): The target storage object (e.g., Wagon, Box, Container).
        data (dict | None): Metadata to add.

    Notes:
        - Automatically ignores None or empty data.
        - Merges keys recursively (non-destructive).
    """
    if not metadata:
        logger.debug("[%s] No metadata provided.", storage.name)
        return

    if not hasattr(storage, "metadata") or storage.metadata is None:
        storage.metadata = {}

    storage.metadata.update(metadata)

    logger.info("[%s] Metadata updated: %s", storage.name, metadata)
