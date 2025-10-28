"""
Forge style types for various data transformation scenarios.
"""

from abc import abstractmethod
from typing import Generic, Any

from pandas.api.types import is_numeric_dtype
from pandas.errors import UndefinedVariableError
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from fragua.style.style import Style, ResultT, register_style
from fragua.utils.logger import get_logger
from fragua.params.forge_params import (
    ForgeParamsT,
    MLForgeParamsT,
    ReportForgeParamsT,
    AnalysisForgeParamsT,
)

logger = get_logger(__name__)

action: str = "forge"


# ---------------------------------------------------------------------- #
# Base ForgeStyle
# ---------------------------------------------------------------------- #
class ForgeStyle(Style[ForgeParamsT, ResultT], Generic[ForgeParamsT, ResultT]):
    """
    Base class for ForgeStyles.

    Standard pipeline provided by Style:
        validate_params -> _run -> validate_result -> postprocess
    """

    # ---------------------------------------------------------------------- #
    # Abstract forge method (subclasses implement this)
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def forge(self, params: ForgeParamsT) -> ResultT:
        """
        Transform the input data according to params.
        Must be implemented by subclasses.
        """
        raise NotImplementedError

    # ---------------------------------------------------------------------- #
    # Internal _run implementation for Style
    # ---------------------------------------------------------------------- #
    def _run(self, params: ForgeParamsT) -> ResultT:
        """
        Executes the ForgeStyle transformation step.

        This method is called by Style.use().
        """
        logger.debug("Starting ForgeStyle '%s' transformation.", self.style_name)
        result = self.forge(params)
        logger.debug("ForgeStyle '%s' transformation completed.", self.style_name)
        return result

    # ---------------------------------------------------------------------- #
    # Utilities for DataFrames
    # ---------------------------------------------------------------------- #
    def fill_missing(
        self,
        df: pd.DataFrame,
        numeric_fill: str = "mean",
        categorical_fill: str = "unknown",
    ) -> None:
        """Fill missing values in DataFrame."""
        for col in df.columns:
            if is_numeric_dtype(df[col]):
                fill_value = df[col].mean() if numeric_fill == "mean" else 0
                df[col] = df[col].fillna(fill_value)
            else:
                df[col] = df[col].fillna(categorical_fill)
        logger.info("%s: Missing values filled.", self.style_name)

    def standardize(self, df: pd.DataFrame) -> None:
        """Standardize string columns (strip spaces and lowercase)."""
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        logger.info("%s: String columns standardized.", self.style_name)


# ---------------- MLForge ----------------
@register_style(action, "forge_ml")
class MLForgeStyle(ForgeStyle[MLForgeParamsT, pd.DataFrame]):
    """Forge style for machine learning preprocessing."""

    def forge(self, params: MLForgeParamsT) -> pd.DataFrame:
        df = params.data

        df = df.copy()

        self.fill_missing(df, numeric_fill="mean")
        self.standardize(df)
        self._encode_categoricals(df)
        self._treat_outliers(df, params.outlier_threshold)
        self._scale_numeric(df)

        logger.info(
            "%s: forge process completed with %d columns.",
            self.style_name,
            len(df.columns),
        )
        return df

    def _encode_categoricals(self, df: pd.DataFrame) -> None:
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

    def _scale_numeric(self, df: pd.DataFrame) -> None:
        num_cols = df.select_dtypes(include="number").columns
        if len(num_cols) > 0:
            scaler = MinMaxScaler()
            df[num_cols] = scaler.fit_transform(df[num_cols])
            logger.debug(
                "%s: Scaled numeric columns: %s", self.style_name, list(num_cols)
            )
        logger.info("%s: Numeric columns scaled.", self.style_name)

    def _treat_outliers(self, df: pd.DataFrame, threshold: float | None = None) -> None:
        num_cols = df.select_dtypes(include="number").columns
        factor = threshold if threshold is not None else 1.5
        for col in num_cols:
            Q1, Q3 = df[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            df[col] = np.clip(df[col], Q1 - factor * IQR, Q3 + factor * IQR)
        logger.info("%s: Outliers treated with factor %.2f.", self.style_name, factor)


# ---------------- ReportForge ----------------
@register_style(action, "forge_report")
class ReportForgeStyle(ForgeStyle[ReportForgeParamsT, pd.DataFrame]):
    """Forge style for reporting transformations."""

    def forge(self, params: ReportForgeParamsT) -> pd.DataFrame:
        df = params.data

        df = df.copy()

        self.fill_missing(df, numeric_fill="zero")
        self.standardize(df)
        self._add_derived_columns(df, params.derived_columns)
        self._format_for_report(df, params.rounding_precision)

        logger.info(
            "%s: forge process completed with %d rows.", self.style_name, len(df)
        )
        return df

    def _add_derived_columns(
        self, df: pd.DataFrame, derived_columns: dict[str, str] | None
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
                except (UndefinedVariableError, SyntaxError, TypeError) as e:
                    logger.warning(
                        "%s: Could not compute derived column '%s': %s",
                        self.style_name,
                        new_col,
                        e,
                    )
        elif {"quantity", "price"}.issubset(df.columns):
            df["total"] = df["quantity"] * df["price"]
            logger.debug("%s: Added derived column 'total'.", self.style_name)

    def _format_for_report(
        self, df: pd.DataFrame, rounding_precision: int | None
    ) -> None:
        obj_cols = df.select_dtypes(include="object").columns
        for col in obj_cols:
            df[col] = df[col].astype(str).str.strip()

        num_cols = df.select_dtypes(include="number").columns
        precision = rounding_precision if rounding_precision is not None else 2
        for col in num_cols:
            df[col] = df[col].round(precision)

        logger.info("%s: Column formatting applied.", self.style_name)


# ---------------- AnalysisForge ----------------
@register_style(action, "forge_analysis")
class AnalysisForgeStyle(ForgeStyle[AnalysisForgeParamsT, pd.DataFrame]):
    """Forge style for data analysis transformations."""

    def forge(self, params: AnalysisForgeParamsT) -> pd.DataFrame:
        df = params.data

        df = df.copy()
        groupby_cols: list[Any] = params.groupby_cols or []
        agg_functions: dict[Any, Any] = params.agg_functions or {}
        sort_by: list[Any] = params.sort_by or []

        self.fill_missing(df, numeric_fill="mean")
        self.standardize(df)

        if groupby_cols:
            if agg_functions:
                df = df.groupby(groupby_cols).agg(agg_functions).reset_index()
            else:
                df = df.groupby(groupby_cols).agg("sum").reset_index()

        if sort_by:
            df = df.sort_values(by=sort_by)

        logger.info("%s: analysis completed with %d rows.", self.style_name, len(df))
        return df
