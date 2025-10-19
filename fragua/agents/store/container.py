"""
Containers for storing loaded data before final delivery.

Containers allow versioned storage of data that has been processed and is ready for delivery.
"""

from typing import Generic, TypeVar, Callable, Optional
from datetime import datetime, timezone
import pandas as pd
from fragua.utils.metrics import calculate_checksum

T = TypeVar("T")


class Container(Generic[T]):
    """
    Container: stores final data ready for delivery
    with metadata, validation, and optional postprocessing.
    """

    def __init__(self, name: str, data: Optional[T] = None):
        self.name = name
        self._stored_at = datetime.now(timezone.utc)
        self.data: Optional[T] = None
        self._checksum: Optional[str] = None
        if data is not None:
            self.store(data)

    def store(self, data: T, postprocess: Optional[Callable[[T], T]] = None) -> None:
        if isinstance(data, list):
            data = pd.DataFrame(data)
        if postprocess:
            data = postprocess(data)
        self.data = data
        self._checksum = calculate_checksum(self.data)

    def retrieve(self) -> Optional[T]:
        return self.data

    @property
    def metadata(self) -> dict[str, object]:
        return {
            "name": self.name,
            "stored_at": self._stored_at,
            "checksum": self._checksum,
            "type": type(self.data).__name__ if self.data is not None else None,
        }

    def __repr__(self) -> str:
        return f"<Container name={self.name} data={'set' if self.data is not None else 'empty'}>"
