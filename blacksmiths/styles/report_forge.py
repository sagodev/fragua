"""ReportForge: transformations for reporting."""

import hashlib
from datetime import datetime
import logging
import pandas as pd
from storage.bagons import Bagon
from blacksmiths.styles.base_style import ForgeStyle

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ReportForge(ForgeStyle):
    """
    Prepares Bagons for reporting:
    - Fill missing with zero
    - Standardize strings
    - Add derived columns
    - Format strings and numeric columns for presentation
    """

    def transform(self, bagon: Bagon) -> Bagon:
        df = bagon.data.copy()

        self._fill_missing(df)
        self._standardize(df)
        self._add_derived_columns(df)
        self._format_for_report(df)
        self._add_metadata(df)

        return Bagon(name=bagon.name, data=df)

    def _fill_missing(self, df: pd.DataFrame):
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(0, inplace=True)
            else:
                df[col].fillna("unknown", inplace=True)
        logger.info("ReportForge: Missing values filled.")

    def _standardize(self, df: pd.DataFrame):
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        logger.info("ReportForge: String columns standardized.")

    def _add_derived_columns(self, df: pd.DataFrame):
        if {"quantity", "price"}.issubset(df.columns):
            df["total"] = df["quantity"] * df["price"]
        logger.info("ReportForge: Derived columns added.")

    def _format_for_report(self, df: pd.DataFrame):
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].str.title()
        for col in df.select_dtypes(include="number").columns:
            df[col] = df[col].round(2)
        logger.info("ReportForge: Formatting for report completed.")

    def _add_metadata(self, df: pd.DataFrame):
        checksum = hashlib.sha256(
            pd.util.hash_pandas_object(df, index=True).values
        ).hexdigest()
        df["_forge_name"] = "ReportForge"
        df["_transform_timestamp"] = datetime.utcnow()
        df["_checksum"] = checksum
