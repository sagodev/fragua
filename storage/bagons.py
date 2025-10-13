"""Bagon: temporary container for extracted data."""

from typing import Any, Dict
from dataclasses import dataclass, field
from datetime import datetime
import pandas as pd


@dataclass
class Bagon:
    """
    Container for extracted data.

    Attributes:
        name: logical name of this bagon (e.g., 'sales_csv').
        data: pandas.DataFrame with the extracted rows.
        metadata: dictionary for storing source, timing, row counts, etc.
    """

    name: str
    data: pd.DataFrame
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # fill sensible metadata fields
        self.metadata.setdefault("created_at", datetime.utcnow().isoformat())
        self.metadata.setdefault("rows", len(self.data) if self.data is not None else 0)

    def preview(self, n: int = 5) -> pd.DataFrame:
        """Return the first `n` rows (convenience)."""
        return self.data.head(n)
