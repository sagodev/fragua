"""
Containers for storing loaded data before final delivery.

Containers allow versioned storage of data that has been processed and is ready for delivery.
"""

from datetime import datetime
import hashlib
import pandas as pd


class Container:
    """
    Container: stores final data ready for delivery with metadata, validation, and optional postprocessing.
    """

    def __init__(self, name: str, data=None):
        self.name = name
        self._stored_at = datetime.utcnow()
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
        self._checksum = hashlib.sha256(
            pd.util.hash_pandas_object(data, index=True).values
        ).hexdigest()

    def retrieve(self):
        return self.data

    @property
    def metadata(self):
        return {
            "name": self.name,
            "stored_at": self._stored_at,
            "checksum": self._checksum,
            "type": type(self.data).__name__ if self.data is not None else None,
        }

    def __repr__(self):
        return f"<Container name={self.name} data={'set' if self.data is not None else 'empty'}>"
