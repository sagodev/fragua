"""
Base storage module for Fragua ETL.

Provides a robust foundation for Box, Container, and Wagon classes
with type validation, checksum calculation, and metadata tracking.
"""

from datetime import datetime, timezone
from typing import Optional, Callable, TypeVar, Generic
import pandas as pd
from fragua.utils.metrics import calculate_checksum

T = TypeVar("T")


class BaseStorage(Generic[T]):
    """
    Base class for storage objects like Box, Container, and Wagon.

    Stores data with optional postprocessing, maintains checksum
    and metadata for auditing and validation.
    """

    def __init__(self, name: str, data: Optional[T] = None):
        self.name = name
        self.data: Optional[T] = None
        self._checksum: Optional[str] = None
        self._stored_at: Optional[datetime] = None

        if data is not None:
            self.store(data)

    def store(self, data: T, postprocess: Optional[Callable[[T], T]] = None) -> None:
        """Store data with optional postprocessing and update checksum."""
        if data is None:
            raise ValueError(f"{self.__class__.__name__}: Cannot store None data")

        if isinstance(data, list):
            data = pd.DataFrame(data)
        elif not isinstance(data, pd.DataFrame):
            raise TypeError(
                f"{self.__class__.__name__}: data must be a list or DataFrame"
            )

        if postprocess:
            data = postprocess(data)
            if data is None:
                raise ValueError(
                    f"{self.__class__.__name__}: Postprocess returned None"
                )

        self.data = data
        self._checksum = calculate_checksum(self.data)
        self._stored_at = datetime.now(timezone.utc)

    def retrieve(self) -> Optional[T]:
        """Retrieve stored data."""
        return self.data

    @property
    def checksum(self) -> Optional[str]:
        """Get the checksum of the stored data."""
        return self._checksum

    @property
    def stored_at(self) -> Optional[datetime]:
        """Get the timestamp when the data was stored."""
        return self._stored_at

    @property
    def metadata(self) -> dict[str, object]:
        """Get metadata about the storage object."""
        return {
            "name": self.name,
            "checksum": self._checksum,
            "stored_at": self._stored_at,
            "rows": getattr(self.data, "shape", (None, None))[0],
            "columns": getattr(self.data, "shape", (None, None))[1],
            "type": type(self.data).__name__ if self.data is not None else None,
        }
