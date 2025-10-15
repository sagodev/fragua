"""
Boxes for storing transformed data from Blacksmiths.

Boxes provide versioned storage for transformed data before loading.
"""

from datetime import datetime
import pandas as pd
from utils.metrics import calculate_checksum


class Box:
    """
    Box: container for transformed data with metadata, validation, and optional postprocessing.
    """

    def __init__(self, name: str, data=None):
        self.name = name
        self._processed_at = datetime.utcnow()
        self.data = None
        self._checksum = None
        if data is not None:
            self.store(data)

    def store(self, data, postprocess=None):
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
            "processed_at": self._processed_at,
            "checksum": self._checksum,
            "type": type(self.data).__name__ if self.data is not None else None,
        }

    def __repr__(self):
        return (
            f"<Box name={self.name} data={'set' if self.data is not None else 'empty'}>"
        )
