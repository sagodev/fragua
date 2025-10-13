"""BasicForge: simple transformations for testing."""

from blacksmiths.styles.base_style import ForgeStyle
from storage.bagons import Bagon
import pandas as pd


class BasicForge(ForgeStyle):
    """
    BasicForge performs simple cleaning:
    - Fill NA in numeric columns with 0
    - Fill NA in object (string) columns with empty string
    - Strip string columns
    - Ensure column names are lowercase
    """

    def transform(self, bagon: Bagon) -> Bagon:
        df = bagon.data.copy()

        # Lowercase columns
        df.columns = [c.lower() for c in df.columns]

        # Fill NA: numeric columns -> 0, object columns -> ""
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(0)
            elif pd.api.types.is_object_dtype(df[col]):
                df[col] = df[col].fillna("").str.strip()

        bagon.data = df
        return bagon
