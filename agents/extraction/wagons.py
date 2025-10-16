"""
Wagons for storing extracted data from Miners.

Wagons provide temporary storage and versioning for raw data.
"""

from datetime import datetime, UTC
import pandas as pd
from utils.metrics import calculate_checksum


class Wagon:
    """
    Wagon: container for extracted data with metadata, validation, and optional postprocessing.
    """

    def __init__(self, name: str, data=None):
        self.name = name
        self._created_at = datetime.now(UTC)
        self.data = None
        self._checksum = None
        if data is not None:
            self.store(data)

    def store(self, data, postprocess=None):
        """Store data in the Wagon, optionally applying postprocess."""
        if data is None:
            raise ValueError("Cannot store None data in Wagon")

        # Convert list of dicts to DataFrame
        if isinstance(data, list):
            data = pd.DataFrame(data)

        if postprocess:
            data = postprocess(data)

        self.data = data
        self._checksum = calculate_checksum(self.data)

    def retrieve(self):
        return self.data

    @property
    def metadata(self):
        return {
            "name": self.name,
            "created_at": self._created_at,
            "checksum": self._checksum,
            "type": type(self.data).__name__ if self.data is not None else None,
        }

    def __repr__(self):
        return f"<Wagon name={self.name} data={'set' if self.data is not None else 'empty'}>"
