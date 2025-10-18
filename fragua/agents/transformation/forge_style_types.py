"""
Concrete ForgeStyle subclasses for Fragua Blacksmiths.
Includes MLForge, ReportForge, and AnalysisForge.
"""

from typing import Any, Dict, TypedDict, NotRequired
import numpy as np
import pandas as pd
from pandas import DataFrame
from sklearn.preprocessing import MinMaxScaler

from fragua.agents.transformation.forge_style import ForgeStyle, register_forge_style
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class MLSourceParams(TypedDict, total=False):
    """ML transformation source parameters."""

    data: DataFrame
    target_column: NotRequired[str]
    categorical_cols: NotRequired[list[str]]
    numeric_cols: NotRequired[list[str]]
    outlier_threshold: NotRequired[float]


class ReportSourceParams(TypedDict, total=False):
    """Report transformation source parameters."""

    data: DataFrame
    format_config: NotRequired[Dict[str, Any]]
    derived_columns: NotRequired[Dict[str, str]]
    rounding_precision: NotRequired[int]


class AnalysisSourceParams(TypedDict, total=False):
    """Analysis transformation source parameters."""

    data: DataFrame
    groupby_cols: NotRequired[list[str]]
    agg_functions: NotRequired[Dict[str, str]]
    sort_by: NotRequired[list[str]]


# ---------------- MLForge ----------------
@register_forge_style("ml")
class MLStyle(ForgeStyle):
    """Forge style for machine learning preprocessing."""

    def __init__(self, style_name: str) -> None:
        super().__init__(style_name=style_name)

    def forge(self, source_params: Dict[str, Any]) -> DataFrame:
        """Transform data for machine learning.

        Args:
            source_params: Dictionary containing:
                data (DataFrame): Data to transform
                target_column (str, optional): Target variable name
                categorical_cols (list[str], optional): Categorical columns to encode
                numeric_cols (list[str], optional): Numeric columns to scale
                outlier_threshold (float, optional): IQR multiplier for outliers

        Returns:
            DataFrame: Transformed data ready for ML

        Raises:
            ValueError: If data is missing or invalid
            TypeError: If data is not a DataFrame
        """
        data = source_params["data"]
        if not isinstance(data, DataFrame):
            raise TypeError("MLStyle requires a pandas DataFrame")

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
class ReportStyle(ForgeStyle):
    """Forge style for reporting transformations."""

    def __init__(self, style_name: str) -> None:
        super().__init__(style_name=style_name)

    def forge(self, source_params: Dict[str, Any]) -> DataFrame:
        """Transform data for reporting.

        Args:
            source_params: Dictionary containing:
                data (DataFrame): Data to transform
                format_config (dict, optional): Column formatting options
                derived_columns (dict, optional): Column calculations
                rounding_precision (int, optional): Decimal places

        Returns:
            DataFrame: Transformed data ready for reporting

        Raises:
            ValueError: If data is missing or invalid
            TypeError: If data is not a DataFrame
        """
        data = source_params["data"]
        if not isinstance(data, DataFrame):
            raise TypeError("ReportStyle requires a pandas DataFrame")

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
        # Format object columns
        obj_cols = df.select_dtypes(include="object").columns
        for col in obj_cols:
            df[col] = df[col].astype(str).str.strip()

        # Format numeric columns
        num_cols = df.select_dtypes(include="number").columns
        for col in num_cols:
            df[col] = df[col].round(2)

        logger.info("%s: Column formatting applied.", self.style_name)


# ---------------- AnalysisForge ----------------
@register_forge_style("analysis")
class AnalysisStyle(ForgeStyle):
    """Forge style for data analysis transformations."""

    def __init__(self, style_name: str) -> None:
        super().__init__(style_name=style_name)

    def forge(self, source_params: Dict[str, Any]) -> DataFrame:
        """Transform data for analysis.

        Args:
            source_params: Dictionary containing:
                data (DataFrame): Data to analyze
                groupby_cols (list[str], optional): Columns to group by
                agg_functions (dict, optional): Aggregation functions
                sort_by (list[str], optional): Columns to sort by

        Returns:
            DataFrame: Transformed data ready for analysis

        Raises:
            ValueError: If data is missing or invalid
            TypeError: If data is not a DataFrame
        """
        data = source_params["data"]
        if not isinstance(data, DataFrame):
            raise TypeError("AnalysisStyle requires a pandas DataFrame")

        df: DataFrame = data.copy()
        groupby_cols = source_params.get("groupby_cols", [])
        agg_functions = source_params.get("agg_functions", {})
        sort_by = source_params.get("sort_by", [])

        # Clean and prepare
        self._fill_missing(df, numeric_fill="mean")
        self._standardize(df)

        # Group and aggregate if specified
        if groupby_cols:
            if agg_functions:
                df = df.groupby(groupby_cols).agg(agg_functions).reset_index()
            else:
                df = df.groupby(groupby_cols).agg("sum").reset_index()

        # Sort if specified
        if sort_by:
            df = df.sort_values(by=sort_by)

        self._add_metadata(df)

        logger.info("%s: analysis completed with %d rows.", self.style_name, len(df))
        return df
