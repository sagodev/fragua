"""
Wagons for storing extracted data from Miners.

Wagons provide temporary storage and versioning for raw data.
"""

import hashlib
import json
from datetime import datetime
import pandas as pd


class Wagon:
    """
    Wagon: container for extracted data with metadata, validation, and optional postprocessing.
    """

    def __init__(self, name: str, data=None):
        self.name = name
        self._created_at = datetime.utcnow()
        self.data = None
        self._checksum = None
        if data is not None:
            self.store(data)

    def store(self, data, postprocess=None):
        # Convert list of dicts to DataFrame
        if isinstance(data, list):
            data = pd.DataFrame(data)

        if postprocess:
            data = postprocess(data)

        self.data = data

        # Compute checksum
        if isinstance(self.data, pd.DataFrame):
            self._checksum = hashlib.sha256(
                pd.util.hash_pandas_object(self.data, index=True).values
            ).hexdigest()
        else:
            # For dicts or other objects
            self._checksum = hashlib.sha256(
                json.dumps(self.data, sort_keys=True).encode()
            ).hexdigest()

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
