"""AnalysisForge: transformations for exploratory data analysis."""

import hashlib
from datetime import datetime
import logging
import pandas as pd
from storage.bagons import Bagon
from blacksmiths.styles.base_style import ForgeStyle

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AnalysisForge(ForgeStyle):
    """
    Performs transformations suitable for analysis:
    - Fill missing values with mean
    - Standardize string columns
    - Add derived columns for totals and rates
    """

    def transform(self, bagon: Bagon) -> Bagon:
        df = bagon.data.copy()

        self._fill_missing(df)
        self._standardize(df)
        self._add_derived_columns(df)
        self._add_metadata(df, bagon.name)

        return Bagon(name=bagon.name, data=df)

    def _fill_missing(self, df: pd.DataFrame):
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(df[col].mean(), inplace=True)
            else:
                df[col].fillna("unknown", inplace=True)
        logger.info("AnalysisForge: Missing values filled.")

    def _standardize(self, df: pd.DataFrame):
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        logger.info("AnalysisForge: String columns standardized.")

    def _add_derived_columns(self, df: pd.DataFrame):
        if {"quantity", "price"}.issubset(df.columns):
            df["total"] = df["quantity"] * df["price"]
        if {"total", "discount_rate"}.issubset(df.columns):
            df["discounted_total"] = df["total"] * (1 - df["discount_rate"])
        logger.info("AnalysisForge: Derived columns added.")

    def _add_metadata(self, df: pd.DataFrame, name: str):
        checksum = hashlib.sha256(
            pd.util.hash_pandas_object(df, index=True).values
        ).hexdigest()
        df["_forge_name"] = "AnalysisForge"
        df["_transform_timestamp"] = datetime.utcnow()
        df["_checksum"] = checksum
