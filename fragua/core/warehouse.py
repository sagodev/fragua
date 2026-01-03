"""Runtime warehouse for execution results."""

from __future__ import annotations
from typing import Any, Dict
from datetime import datetime

from fragua.core.box import FraguaBox


class FraguaWarehouse:
    """
    In-memory warehouse for execution results.

    Stores FraguaBox outputs produced by agents during ETL testing.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._records: Dict[str, Dict[str, Any]] = {}

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

    def get(self, key: str) -> FraguaBox:
        """Retrieve the stored result by key."""
        return self._records[key]["result"]

    def get_record(self, key: str) -> Dict[str, Any]:
        """Retrieve the full stored record."""
        return dict(self._records[key])

    def list_keys(self) -> list[str]:
        """List all stored keys."""
        return list(self._records.keys())

    def snapshot(self) -> Dict[str, Dict[str, FraguaBox]]:
        """Return a shallow copy of all records."""
        return dict(self._records)

    def clear(self) -> None:
        """Clear all stored results."""
        self._records.clear()

    def __len__(self) -> int:
        return len(self._records)
