"""
Transform parameters classes for different types of data transformations.
"""

from typing import Any, Dict
from pandas import DataFrame
from fragua.transform.params.base import TransformParams

# pylint: disable=too-many-arguments, too-many-positional-arguments


class MLTransformParams(TransformParams):
    """Parameters for machine learning transformations."""

    target_column: str | None
    categorical_cols: list[str]
    numeric_cols: list[str]
    outlier_threshold: float | None

    purpose = (
        "Transformation parameters used to prepare data for machine learning tasks."
    )

    FIELD_DESCRIPTIONS = {
        "data": "Input DataFrame containing the dataset.",
        "target_column": "Column to be predicted by machine learning models.",
        "categorical_cols": "List of columns treated as categorical variables.",
        "numeric_cols": "List of columns treated as numeric variables.",
        "outlier_threshold": "Threshold used to trim or detect outliers.",
    }

    def __init__(
        self,
        data: DataFrame,
        target_column: str | None = None,
        categorical_cols: list[str] | None = None,
        numeric_cols: list[str] | None = None,
        outlier_threshold: float | None = None,
    ) -> None:
        super().__init__(style="ml", data=data)
        self.target_column = target_column
        self.categorical_cols = categorical_cols or []
        self.numeric_cols = numeric_cols or []
        self.outlier_threshold = outlier_threshold


class ReportTransformParams(TransformParams):
    """Parameters for report generation transformations."""

    format_config: Dict[str, Any]
    derived_columns: Dict[str, str]
    rounding_precision: int | None

    purpose = "Parameters used to prepare, derive, and format data for reporting."

    FIELD_DESCRIPTIONS = {
        "data": "Input DataFrame before formatting.",
        "format_config": "Rules for formatting the output (alignment, styles, etc).",
        "derived_columns": "New columns generated using formulas or expressions.",
        "rounding_precision": "Number of decimal places to round numeric values.",
    }

    def __init__(
        self,
        data: DataFrame,
        format_config: Dict[str, Any] | None = None,
        derived_columns: Dict[str, str] | None = None,
        rounding_precision: int | None = None,
    ) -> None:
        super().__init__(style="report", data=data)
        self.format_config = format_config or {}
        self.derived_columns = derived_columns or {}
        self.rounding_precision = rounding_precision


class AnalysisTransformParams(TransformParams):
    """Parameters for data analysis transformations."""

    groupby_cols: list[str]
    agg_functions: Dict[str, str]
    sort_by: list[str]

    purpose = "Parameters for performing analytical operations such as groupby and aggregation."

    FIELD_DESCRIPTIONS = {
        "data": "Input DataFrame to analyze.",
        "groupby_cols": "Columns used for grouping the data.",
        "agg_functions": "Aggregation functions to apply to grouped data.",
        "sort_by": "Columns used to sort the resulting aggregated data.",
    }

    def __init__(
        self,
        data: DataFrame,
        groupby_cols: list[str] | None = None,
        agg_functions: Dict[str, str] | None = None,
        sort_by: list[str] | None = None,
    ) -> None:
        super().__init__(style="analysis", data=data)
        self.groupby_cols = groupby_cols or []
        self.agg_functions = agg_functions or {}
        self.sort_by = sort_by or []
