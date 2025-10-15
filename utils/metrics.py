import hashlib
import json
from typing import Any
import pandas as pd


def _serialize_dataframe(df: pd.DataFrame) -> bytes:
    # Make a copy and sort columns to guarantee deterministic ordering
    df_copy = df.copy()
    # ensure reproducible column order
    cols = sorted(df_copy.columns.tolist())
    df_copy = df_copy[cols]
    # Use to_csv without index to avoid index differences
    return df_copy.to_csv(index=False).encode("utf-8")


def _serialize_other(obj: Any) -> bytes:
    if isinstance(obj, (dict, list)):
        return json.dumps(obj, sort_keys=True, default=str).encode("utf-8")
    return str(obj).encode("utf-8")


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
