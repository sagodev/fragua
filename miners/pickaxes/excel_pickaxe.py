"""Excel pickaxe - reads Excel files into a Bagon."""

from typing import Optional
import pandas as pd
from ...miners.pickaxes.base_pickaxe import Pickaxe
from ...storage.bagons import Bagon

class ExcelPickaxe(Pickaxe):
    """
    ExcelPickaxe extracts data from Excel files.

    Args:
        path: filesystem path to Excel file.
        sheet_name: sheet to read (default 0).
        read_kwargs: forwarded kwargs to pandas.read_excel.
    """
    def __init__(self, path: str, sheet_name: Optional[str|int] = 0, name: Optional[str] = None, read_kwargs: Optional[dict] = None):
        super().__init__(name=name or f"excel:{path}")
        self.path = path
        self.sheet_name = sheet_name
        self.read_kwargs = read_kwargs or {}

    def extract(self) -> Bagon:
        df = pd.read_excel(self.path, sheet_name=self.sheet_name, **self.read_kwargs)
        bagon = Bagon(name=self.name, data=df)
        bagon.metadata.update({"source": "excel", "path": self.path, "sheet": self.sheet_name})
        return bagon
