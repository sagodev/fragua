"""
Concrete ForgeStyle subclasses for Fragua Blacksmiths.
Includes MLForge, ReportForge, and AnalysisForge.
"""

from typing import Dict
import numpy as np
import pandas as pd
from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler

from agents.transformation.forge_style import ForgeStyle, register_forge_style
from utils.logger import get_logger

logger = get_logger(__name__)


# ---------------- MLForge ----------------
@register_forge_style("ml")
class MLStyle(ForgeStyle[DataFrame, DataFrame]):
    """Forge style for machine learning preprocessing."""

    def forge(self, source: Dict[str, DataFrame]) -> DataFrame:
        data: DataFrame = source["data"]
        df: DataFrame = data.copy()

        self._fill_missing(df, numeric_fill="mean")
        self._standardize(df)
        self._encode_categoricals(df)
        self._treat_outliers(df)
        self._scale_numeric(df)
        self._add_metadata(df)

        logger.info(
            "%s: forge process completed with %d columns.",
            self.style_name,
            len(df.columns),
        )
        return df

    def _encode_categoricals(self, df: DataFrame) -> None:
        cat_cols = df.select_dtypes(include="object").columns
        if len(cat_cols) > 0:
            df_dummies = pd.get_dummies(df[cat_cols], dummy_na=False)
            df.drop(columns=cat_cols, inplace=True)
            for col in df_dummies.columns:
                df[col] = df_dummies[col]
            logger.debug(
                "%s: Encoded categorical columns: %s", self.style_name, list(cat_cols)
            )
        logger.info("%s: Categoricals encoded.", self.style_name)

    def _scale_numeric(self, df: DataFrame) -> None:
        num_cols = df.select_dtypes(include="number").columns
        if len(num_cols) > 0:
            scaler = MinMaxScaler()
            df[num_cols] = scaler.fit_transform(df[num_cols])
            logger.debug(
                "%s: Scaled numeric columns: %s", self.style_name, list(num_cols)
            )
        logger.info("%s: Numeric columns scaled.", self.style_name)

    def _treat_outliers(self, df: pd.DataFrame):
        num_cols = df.select_dtypes(include="number").columns
        for col in num_cols:
            Q1, Q3 = df[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            df[col] = np.clip(df[col], Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)
        logger.info("%s: Outliers treated.", self.style_name)


# ---------------- ReportForge ----------------
@register_forge_style("report")
class ReportStyle(ForgeStyle[DataFrame, DataFrame]):
    """Forge style for reporting transformations."""

    def forge(self, source: Dict[str, DataFrame]) -> DataFrame:
        data: DataFrame = source["data"]
        df: DataFrame = data.copy()

        self._fill_missing(df, numeric_fill="zero")
        self._standardize(df)
        self._add_derived_columns(df)
        self._format_for_report(df)
        self._add_metadata(df)

        logger.info(
            "%s: forge process completed with %d rows.", self.style_name, len(df)
        )
        return df

    def _add_derived_columns(self, df: DataFrame) -> None:
        if {"quantity", "price"}.issubset(df.columns):
            df["total"] = df["quantity"] * df["price"]
            logger.debug("%s: Added derived column 'total'.", self.style_name)
        logger.info("%s: Derived columns added.", self.style_name)

    def _format_for_report(self, df: DataFrame) -> None:
        obj_cols = df.select_dtypes(include="object").columns
        num_cols = df.select_dtypes(include="number").columns

        for col in obj_cols:
            df[col] = df[col].astype(str).str.title()
        for col in num_cols:
            df[col] = df[col].round(2)

        logger.debug(
            "%s: Formatted columns for report: %s", self.style_name, list(df.columns)
        )
        logger.info("%s: Formatting for report completed.", self.style_name)


# ---------------- AnalysisForge ----------------
@register_forge_style("analysis")
class AnalysisStyle(ForgeStyle[DataFrame, DataFrame]):
    """Forge style for analytical transformations."""

    def forge(self, source: Dict[str, DataFrame]) -> DataFrame:
        data: DataFrame = source["data"]
        df: DataFrame = data.copy()

        self._fill_missing(df, numeric_fill="mean")
        self._standardize(df)
        self._add_derived_columns(df)
        self._add_metadata(df)

        logger.info(
            "%s: forge process completed with shape %s.", self.style_name, df.shape
        )
        return df

    def _add_derived_columns(self, df: DataFrame) -> None:
        added: list[str] = []

        if {"quantity", "price"}.issubset(df.columns):
            df["total"] = df["quantity"] * df["price"]
            added.append("total")

        if {"total", "discount_rate"}.issubset(df.columns):
            df["discounted_total"] = df["total"] * (1 - df["discount_rate"])
            added.append("discounted_total")

        logger.debug("%s: Added derived columns: %s", self.style_name, added)
        logger.info("%s: Derived columns added.", self.style_name)
