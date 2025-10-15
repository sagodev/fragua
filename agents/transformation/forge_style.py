"""
Base ForgeStyle class for Fragua Blacksmiths.
Contains common utilities for transformations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging
import pandas as pd
from utils.metrics import calculate_checksum


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Registry for dynamic ForgeStyle discovery
FORGESTYLE_REGISTRY: dict[str, type] = {}


def register_forge_style(name: str):
    """
    Decorator to register a ForgeStyle subclass dynamically.

    Usage:
        @register_forge_style("ml")
        class MLForge(ForgeStyle):
            ...
    """

    def wrapper(cls):
        FORGESTYLE_REGISTRY[name] = cls
        return cls

    return wrapper


class ForgeStyle(ABC):
    """
    Base class for ForgeStyles.
    Provides common utilities for transformations.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def use(self, data):
        """
        Main transformation method. Must be implemented by subclasses.
        """
        pass

    def _fill_missing(
        self, df: pd.DataFrame, numeric_fill="mean", categorical_fill="unknown"
    ):
        """
        Fill missing values in DataFrame.
        """
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                if numeric_fill == "mean":
                    df[col].fillna(df[col].mean(), inplace=True)
                elif numeric_fill == "zero":
                    df[col].fillna(0, inplace=True)
            else:
                df[col].fillna(categorical_fill, inplace=True)
        logger.info(f"{self.name}: Missing values filled.")

    def _standardize(self, df: pd.DataFrame):
        """
        Standardize string columns (strip spaces and lowercase).
        """
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        logger.info(f"{self.name}: String columns standardized.")

    def _add_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add metadata columns to the transformed dataframe.
        """
        checksum_value = calculate_checksum(df)
        df["_forge_name"] = self.name
        df["_transform_timestamp"] = datetime.utcnow()
        df["_checksum"] = checksum_value

        self.metadata["checksum"] = checksum_value
        return df
