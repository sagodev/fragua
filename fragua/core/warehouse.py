"""Runtime warehouse for execution results."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, List

import pandas as pd

from fragua.core.box import FraguaBox

if TYPE_CHECKING:
    from typing import Dict


class FraguaWarehouse:
    """
    In-memory warehouse for execution results.

    Stores FraguaBox outputs produced by agents during ETL testing.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._records: dict[str, dict[str, Any]] = {}

    def store(self, box: FraguaBox) -> None:
        """
        Store a FraguaBox execution result.

        Parameters
        ----------
        box: FraguaBox
            The execution result container to persist.
        """
        self._records[box.key] = {
            "result": box.result,
            "metadata": box.metadata,
            "created_at": datetime.now(),
        }

    def get(self, key: str) -> dict[str, pd.DataFrame]:
        """Retrieve the stored result by key."""
        return self._records[key]["result"]

    def get_record(self, key: str) -> dict[str, Any]:
        """Retrieve the full stored record."""
        return dict(self._records[key])

    def list_keys(self) -> List[str]:
        """List all stored keys."""
        return list(self._records.keys())

    def snapshot(self) -> dict[str, dict[str, Any]]:
        """Return a shallow copy of all records."""
        return dict(self._records)

    def clear(self) -> None:
        """Clear all stored results."""
        self._records.clear()

    def __len__(self) -> int:
        return len(self._records)
