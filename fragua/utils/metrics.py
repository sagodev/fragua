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
from typing import Any, cast, Optional
import pandas as pd
from fragua.core.base_agent import BaseAgent
from fragua.core.base_params import BaseParams
from fragua.core.base_storage import BaseStorage
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


def normalize_input(agent: BaseAgent[Any, Any], input_data: Any) -> Any:
    """Convert input data into a format compatible with a BaseStyle."""
    if isinstance(input_data, BaseStorage):
        if input_data.data is None:
            raise ValueError(f"{input_data.name} has no data to process")
        logger.debug("[%s] Normalized input from BaseStorage", agent.name)
        return input_data.data
    if isinstance(input_data, pd.DataFrame):
        logger.debug("[%s] Normalized input as DataFrame", agent.name)
        return input_data
    if isinstance(input_data, BaseParams):
        logger.debug("[%s] Normalized input as BaseParams", agent.name)
        return input_data
    logger.debug("[%s] Input normalization returned original data", agent.name)
    return input_data


def add_metadata_to_storage(
    storage: BaseStorage[Any],
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
