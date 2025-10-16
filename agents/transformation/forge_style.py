"""
Base ForgeStyle class for Fragua Blacksmiths.
Contains common utilities for transformations.
"""

from abc import abstractmethod
from typing import Any, Generator
from datetime import datetime, UTC
import pandas as pd

from utils.metrics import calculate_checksum
from utils.logger import get_logger
from core import Style

# Unified logger for ForgeStyle
logger = get_logger(__name__)


def register_forge_style(name: str):
    """
    Decorator to register a ForgeStyle subclass dynamically.
    """

    def wrapper(cls):
        FORGESTYLE_REGISTRY[name] = cls
        logger.debug("Registered ForgeStyle: %s", name)
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

        logger.debug(
            "Starting ForgeStyle '%s' transformation pipeline.", self.style_name
        )

        try:
            data = self.forge(data)
            logger.debug("%s: forge() step completed.", self.style_name)

            data = self.validate(data)
            logger.debug("%s: validate() step completed.", self.style_name)

            data = self.postprocess(data)
            logger.debug("%s: postprocess() step completed.", self.style_name)

            return data

        except Exception as e:
            self.log_error(e)
            raise

    @abstractmethod
    def forge(self, data: Any) -> Generator | Any:
        """Must be implemented by subclasses to transform data."""

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
        logger.info("%s: Missing values filled.", self.style_name)

    def _standardize(self, df: pd.DataFrame):
        """Standardize string columns (strip spaces and lowercase)."""
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        logger.info("%s: String columns standardized.", self.style_name)

    def _add_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add metadata columns to the transformed dataframe."""
        checksum_value = calculate_checksum(df)
        df["_forge_name"] = self.style_name
        df["_transform_timestamp"] = datetime.now(UTC)
        df["_checksum"] = checksum_value

        self.metadata["checksum"] = checksum_value
        logger.debug(
            "%s: Metadata added with checksum %s.", self.style_name, checksum_value
        )
        return df


# Registry for dynamic ForgeStyle discovery
FORGESTYLE_REGISTRY: dict[str, type[ForgeStyle]] = {}
