"""
Boxes for storing transformed data from Blacksmiths.

Boxes provide versioned storage for transformed data before loading.
"""


from typing import Generic, TypeVar, Callable, Optional
from datetime import datetime, UTC
import pandas as pd
from utils.metrics import calculate_checksum

T = TypeVar("T")

class Box(Generic[T]):
    """
    Box: container for transformed data with metadata, validation, and optional postprocessing.
    """

    def __init__(self, name: str, data: Optional[T] = None):
        self.name = name
        self._processed_at = datetime.now(UTC)
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
            "processed_at": self._processed_at,
            "checksum": self._checksum,
            "type": type(self.data).__name__ if self.data is not None else None,
        }

    def __repr__(self) -> str:
        return f"<Box name={self.name} data={'set' if self.data is not None else 'empty'}>"
