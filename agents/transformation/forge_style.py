"""
Base ForgeStyle class for Fragua Blacksmiths.
Contains common utilities for transformations.
"""

from typing import Any, Generator
from datetime import datetime, timezone
import logging
import pandas as pd
from utils.metrics import calculate_checksum
from core import Style

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Registry for dynamic ForgeStyle discovery
FORGESTYLE_REGISTRY: dict[str, type] = {}


def register_forge_style(name: str):
    """
    Decorator to register a ForgeStyle subclass dynamically.
    """

    def wrapper(cls):
        FORGESTYLE_REGISTRY[name] = cls
        return cls

    return wrapper


class ForgeStyle(Style):
    """
    Base class for ForgeStyles.
    Provides common utilities for transformations.
    Inherits from abstract Style.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.metadata: dict[str, Any] = {}

    def use(self, data: Any) -> Any:
        """
        Main transformation method.
        Executes forge -> validate -> postprocess pipeline.
        """
        if data is None:
            raise ValueError("Input data cannot be None")

        try:
            data = self.forge(data)
            data = self.validate(data)
            return self.postprocess(data)
        except Exception as e:
            self.log_error(e)
            raise

    def forge(self, data: Any) -> Generator | Any:
        """Must be implemented by subclasses to transform data."""
        raise NotImplementedError("Subclasses must implement forge()")

    def validate(self, data: Any) -> Any:
        """Basic validation of the data."""
        if data is None:
            raise ValueError("No data extracted")
        return data

    def postprocess(self, data: Any) -> Any:
        """Optional step for cleaning or formatting data."""
        return data

    def log_error(self, error: Exception) -> None:
        """Basic error logging."""
        logger.error(f"[ForgeStyle ERROR] {type(error).__name__}: {error}")

    # ------------------ Utilities for DataFrames ------------------ #

    def _fill_missing(
        self, df: pd.DataFrame, numeric_fill="mean", categorical_fill="unknown"
    ):
        """Fill missing values in DataFrame."""
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                if numeric_fill == "mean":
                    df[col].fillna(df[col].mean(), inplace=True)
                elif numeric_fill == "zero":
                    df[col].fillna(0, inplace=True)
            else:
                df[col].fillna(categorical_fill, inplace=True)
        logger.info(f"{self.style_name}: Missing values filled.")

    def _standardize(self, df: pd.DataFrame):
        """Standardize string columns (strip spaces and lowercase)."""
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        logger.info(f"{self.style_name}: String columns standardized.")

    def _add_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add metadata columns to the transformed dataframe."""
        checksum_value = calculate_checksum(df)
        df["_forge_name"] = self.style_name
        df["_transform_timestamp"] = datetime.now(timezone.utc)
        df["_checksum"] = checksum_value

        self.metadata["checksum"] = checksum_value
        return df
