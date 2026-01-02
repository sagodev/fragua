"""Runtime warehouse for execution results."""

from __future__ import annotations
from typing import Any, Dict, Optional
from datetime import datetime


class FraguaWarehouse:
    """
    In-memory warehouse for execution results.

    Stores runtime outputs produced by agents during ETL testing.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._records: Dict[str, Dict[str, Any]] = {}

    def store(
        self,
        key: str,
        result: Any,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Store an execution result.

        Parameters
        ----------
        key:
            Logical identifier for the execution (e.g. function name).
        result:
            Execution output.
        metadata:
            Optional execution metadata.
        """
        self._records[key] = {
            "result": result,
            "metadata": metadata or {},
            "created_at": datetime.now(),
        }

    def get(self, key: str) -> Any:
        """Retrieve a stored result by key."""
        return self._records[key]["result"]

    def get_record(self, key: str) -> Dict[str, Any]:
        """Retrieve full execution record."""
        return dict(self._records[key])

    def list_keys(self) -> list[str]:
        """List all stored execution keys."""
        return list(self._records.keys())

    def snapshot(self) -> Dict[str, Dict[str, Any]]:
        """Return a shallow copy of the warehouse."""
        return dict(self._records)

    def clear(self) -> None:
        """Clear all stored results."""
        self._records.clear()

    def __len__(self) -> int:
        return len(self._records)
