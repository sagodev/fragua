"""
Metrics Utilities for Fragua ETL Framework.

This module provides stable and deterministic checksum calculations
for various data structures including pandas DataFrames, dictionaries,
lists, and other Python objects. It ensures reproducible checksums
by serializing the data in a consistent way.
"""

import hashlib
import json
from typing import Any, cast
import pandas as pd


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
