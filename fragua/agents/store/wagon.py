"""
Wagons for storing extracted data from Miners.

Wagons provide temporary storage and versioning for raw data.
"""


from typing import Generic, TypeVar, Callable, Optional
from datetime import datetime, UTC
import pandas as pd
from fragua.utils.metrics import calculate_checksum

T = TypeVar("T")

class Wagon(Generic[T]):
    """
    Wagon: container for extracted data with metadata, validation, and optional postprocessing.
    """

    def __init__(self, name: str, data: Optional[T] = None):
        self.name = name
        self._created_at = datetime.now(UTC)
        self.data: Optional[T] = None
        self._checksum: Optional[str] = None
        if data is not None:
            self.store(data)

    def store(self, data: T, postprocess: Optional[Callable[[T], T]] = None) -> None:
        if data is None:
            raise ValueError("Cannot store None data in Wagon")
        # Convert list of dicts to DataFrame if T is DataFrame
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
            "created_at": self._created_at,
            "checksum": self._checksum,
            "type": type(self.data).__name__ if self.data is not None else None,
        }

    def __repr__(self) -> str:
        return f"<Wagon name={self.name} data={'set' if self.data is not None else 'empty'}>"
