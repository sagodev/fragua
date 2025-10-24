"""
Base storage module for Fragua ETL.

Provides a robust foundation for Box, Container, and Wagon classes
with type validation, checksum calculation, and metadata tracking.
"""

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
        self._operation_metadata: dict[str, object] = (
            {}
        )  # Metadata from agent operation

        if data is not None:
            self.store(data)

    def store(self, data: T, postprocess: Optional[Callable[[T], T]] = None) -> None:
        """
        Store data with optional postprocessing and update checksum.
        """
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

        # Calculate checksum
        self._checksum = calculate_checksum(self.data)

    def retrieve(self) -> Optional[T]:
        """Retrieve stored data."""
        return self.data

    @property
    def checksum(self) -> Optional[str]:
        """Get the checksum of the stored data."""
        return self._checksum

    def attach_metadata(self, metadata: dict[str, object]) -> None:
        """
        Attach operation-related metadata to this storage object.

        Args:
            metadata (dict): Dictionary containing metadata from the agent operation.
        """
        self._operation_metadata.update(metadata)

    @property
    def metadata(self) -> dict[str, object]:
        """
        Return combined metadata, separated into 'base' and 'operation'.

        Returns:
            dict: Dictionary with 'base' and 'operation' keys.
        """
        base_meta = {
            "storage_name": self.name,
            "type": self.__class__.__name__.lower(),
            "rows": getattr(self.data, "shape", (None, None))[0],
            "columns": getattr(self.data, "shape", (None, None))[1],
            "checksum": self._checksum,
        }

        return {"base": base_meta, "operation": self._operation_metadata}

    def __repr__(self) -> str:
        """Return a concise, informative string representation of the storage object."""
        rows = getattr(self.data, "shape", (None, None))[0]
        cols = getattr(self.data, "shape", (None, None))[1]
        return (
            f"<{self.__class__.__name__} name={self.name!r}, "
            f"type={type(self.data).__name__}, "
            f"rows={rows}, cols={cols}, "
            f"checksum={self._checksum}>"
        )
