"""CSV pickaxe - reads CSV files into a Bagon."""

from typing import Optional
import pandas as pd
from ...miners.pickaxes.base_pickaxe import Pickaxe
from ...storage.bagons import Bagon

class CSVPickaxe(Pickaxe):
    """
    CSVPickaxe extracts data from CSV files.

    Args:
        path: filesystem path to CSV.
        read_kwargs: forwarded kwargs to pandas.read_csv.
    """
    def __init__(self, path: str, name: Optional[str] = None, read_kwargs: Optional[dict] = None):
        super().__init__(name=name or f"csv:{path}")
        self.path = path
        self.read_kwargs = read_kwargs or {}

    def extract(self) -> Bagon:
        df = pd.read_csv(self.path, **self.read_kwargs)
        bagon = Bagon(name=self.name, data=df)
        bagon.metadata.update({"source": "csv", "path": self.path})
        return bagon
