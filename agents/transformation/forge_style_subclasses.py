"""
Concrete ForgeStyle subclasses for Fragua Blacksmiths.
Includes MLForge, ReportForge, and AnalysisForge.
"""

import logging
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from agents.transformation.forge_style import ForgeStyle, register_forge_style
from agents.transformation.boxes import Box

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# ---------------- MLForge ----------------
@register_forge_style("ml")
class MLForge(ForgeStyle):
    tool_name = "MLForge"

    def use(self, data) -> Box:
        df = pd.DataFrame(data) if isinstance(data, list) else data.copy()
        self._fill_missing(df, numeric_fill="mean")
        self._standardize(df)
        self._encode_categoricals(df)
        self._treat_outliers(df)
        self._scale_numeric(df)
        self._add_metadata(df)
        return Box(name="MLForge_Result", data=df)

    def _encode_categoricals(self, df: pd.DataFrame):
        cat_cols = df.select_dtypes(include="object").columns
        if len(cat_cols) > 0:
            df_dummies = pd.get_dummies(df[cat_cols], dummy_na=False)
            df.drop(columns=cat_cols, inplace=True)
            df[df_dummies.columns] = df_dummies
        logger.info(f"{self.name}: Categoricals encoded.")

    def _scale_numeric(self, df: pd.DataFrame):
        num_cols = df.select_dtypes(include="number").columns
        if len(num_cols) > 0:
            scaler = MinMaxScaler()
            df[num_cols] = scaler.fit_transform(df[num_cols])
        logger.info(f"{self.name}: Numeric columns scaled.")

    def _treat_outliers(self, df: pd.DataFrame):
        num_cols = df.select_dtypes(include="number").columns
        for col in num_cols:
            Q1, Q3 = df[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            df[col] = np.clip(df[col], Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)
        logger.info(f"{self.name}: Outliers treated.")


# ---------------- ReportForge ----------------
@register_forge_style("report")
class ReportForge(ForgeStyle):
    tool_name = "ReportForge"

    def use(self, data) -> Box:
        df = pd.DataFrame(data) if isinstance(data, list) else data.copy()
        self._fill_missing(df, numeric_fill="zero")
        self._standardize(df)
        self._add_derived_columns(df)
        self._format_for_report(df)
        self._add_metadata(df)
        return Box(name="ReportForge_Result", data=df)

    def _add_derived_columns(self, df: pd.DataFrame):
        if {"quantity", "price"}.issubset(df.columns):
            df["total"] = df["quantity"] * df["price"]
        logger.info(f"{self.name}: Derived columns added.")

    def _format_for_report(self, df: pd.DataFrame):
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].str.title()
        for col in df.select_dtypes(include="number").columns:
            df[col] = df[col].round(2)
        logger.info(f"{self.name}: Formatting for report completed.")


# ---------------- AnalysisForge ----------------
@register_forge_style("analysis")
class AnalysisForge(ForgeStyle):
    tool_name = "AnalysisForge"

    def use(self, data) -> Box:
        df = pd.DataFrame(data) if isinstance(data, list) else data.copy()
        self._fill_missing(df, numeric_fill="mean")
        self._standardize(df)
        self._add_derived_columns(df)
        self._add_metadata(df)
        return Box(name="AnalysisForge_Result", data=df)

    def _add_derived_columns(self, df: pd.DataFrame):
        if {"quantity", "price"}.issubset(df.columns):
            df["total"] = df["quantity"] * df["price"]
        if {"total", "discount_rate"}.issubset(df.columns):
            df["discounted_total"] = df["total"] * (1 - df["discount_rate"])
        logger.info(f"{self.name}: Derived columns added.")
