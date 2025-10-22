"""
Forge style types for various data transformation scenarios.
"""

import numpy as np
import pandas as pd
from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler

from fragua.styles.forge_style import ForgeStyle, register_forge_style
from fragua.params.forge_params import (
    MLForgeParamsT,
    ReportForgeParamsT,
    AnalysisForgeParamsT,
)
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------- MLForge ----------------
@register_forge_style("ml")
class MLForgeStyle(ForgeStyle[MLForgeParamsT, DataFrame]):
    """Forge style for machine learning preprocessing."""

    def forge(self, params: MLForgeParamsT) -> DataFrame:
        df = params.data
        if not isinstance(df, DataFrame):
            raise TypeError("MLForgeStyle requires a pandas DataFrame")

        df = df.copy()

        self._fill_missing(df, numeric_fill="mean")
        self._standardize(df)
        self._encode_categoricals(df)
        self._treat_outliers(df, params.outlier_threshold)
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

    def _treat_outliers(self, df: DataFrame, threshold: float | None = None) -> None:
        num_cols = df.select_dtypes(include="number").columns
        factor = threshold if threshold is not None else 1.5
        for col in num_cols:
            Q1, Q3 = df[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            df[col] = np.clip(df[col], Q1 - factor * IQR, Q3 + factor * IQR)
        logger.info("%s: Outliers treated with factor %.2f.", self.style_name, factor)


# ---------------- ReportForge ----------------
@register_forge_style("report")
class ReportForgeStyle(ForgeStyle[ReportForgeParamsT, DataFrame]):
    """Forge style for reporting transformations."""

    def forge(self, params: ReportForgeParamsT) -> DataFrame:
        df = params.data
        if not isinstance(df, DataFrame):
            raise TypeError("ReportForgeStyle requires a pandas DataFrame")

        df = df.copy()

        self._fill_missing(df, numeric_fill="zero")
        self._standardize(df)
        self._add_derived_columns(df, params.derived_columns)
        self._format_for_report(df, params.rounding_precision)
        self._add_metadata(df)

        logger.info(
            "%s: forge process completed with %d rows.", self.style_name, len(df)
        )
        return df

    def _add_derived_columns(
        self, df: DataFrame, derived_columns: dict[str, str] | None
    ) -> None:
        if derived_columns:
            for new_col, expr in derived_columns.items():
                try:
                    df[new_col] = df.eval(expr)
                    logger.debug(
                        "%s: Derived column '%s' created from expression '%s'.",
                        self.style_name,
                        new_col,
                        expr,
                    )
                except Exception as e:
                    logger.warning(
                        "%s: Could not compute derived column '%s': %s",
                        self.style_name,
                        new_col,
                        e,
                    )
        elif {"quantity", "price"}.issubset(df.columns):
            df["total"] = df["quantity"] * df["price"]
            logger.debug("%s: Added derived column 'total'.", self.style_name)

    def _format_for_report(self, df: DataFrame, rounding_precision: int | None) -> None:
        obj_cols = df.select_dtypes(include="object").columns
        for col in obj_cols:
            df[col] = df[col].astype(str).str.strip()

        num_cols = df.select_dtypes(include="number").columns
        precision = rounding_precision if rounding_precision is not None else 2
        for col in num_cols:
            df[col] = df[col].round(precision)

        logger.info("%s: Column formatting applied.", self.style_name)


# ---------------- AnalysisForge ----------------
@register_forge_style("analysis")
class AnalysisForgeStyle(ForgeStyle[AnalysisForgeParamsT, DataFrame]):
    """Forge style for data analysis transformations."""

    def forge(self, params: AnalysisForgeParamsT) -> DataFrame:
        df = params.data
        if not isinstance(df, DataFrame):
            raise TypeError("AnalysisForgeStyle requires a pandas DataFrame")

        df = df.copy()
        groupby_cols = params.groupby_cols or []
        agg_functions = params.agg_functions or {}
        sort_by = params.sort_by or []

        self._fill_missing(df, numeric_fill="mean")
        self._standardize(df)

        # Group and aggregate if specified
        if groupby_cols:
            if agg_functions:
                df = df.groupby(groupby_cols).agg(agg_functions).reset_index()
            else:
                df = df.groupby(groupby_cols).agg("sum").reset_index()

        if sort_by:
            df = df.sort_values(by=sort_by)

        self._add_metadata(df)
        logger.info("%s: analysis completed with %d rows.", self.style_name, len(df))
        return df
