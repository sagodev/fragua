"""
Transform parameters classes for different types of data transformations.
"""

from typing import Any, Dict, List, Optional, Type
from pandas import DataFrame
from fragua.transform.params.base import TransformParams

# pylint: disable=too-many-arguments, too-many-positional-arguments


class MLTransformParams(TransformParams):
    """Parameters for machine learning transformations."""

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
        data: Optional[DataFrame] = None,
        target_column: Optional[str] = None,
        categorical_cols: Optional[List[str]] = None,
        numeric_cols: Optional[List[str]] = None,
        outlier_threshold: Optional[float] = None,
    ) -> None:
        super().__init__(style="ml", data=data)
        self.target_column = target_column if target_column else ""
        self.categorical_cols = categorical_cols if categorical_cols else []
        self.numeric_cols = numeric_cols if numeric_cols else []
        self.outlier_threshold = outlier_threshold


class ReportTransformParams(TransformParams):
    """Parameters for report generation transformations."""

    purpose = "Parameters used to prepare, derive, and format data for reporting."

    FIELD_DESCRIPTIONS = {
        "data": "Input DataFrame before formatting.",
        "format_config": "Rules for formatting the output (alignment, styles, etc).",
        "derived_columns": "New columns generated using formulas or expressions.",
        "rounding_precision": "Number of decimal places to round numeric values.",
    }

    def __init__(
        self,
        data: Optional[DataFrame] = None,
        format_config: Optional[Dict[str, Any]] = None,
        derived_columns: Optional[Dict[str, str]] = None,
        rounding_precision: Optional[int] = None,
    ) -> None:
        super().__init__(style="report", data=data)
        self.format_config = format_config if format_config else {}
        self.derived_columns = derived_columns if derived_columns else {}
        self.rounding_precision = rounding_precision if rounding_precision else 2


class AnalysisTransformParams(TransformParams):
    """Parameters for data analysis transformations."""

    purpose = "Parameters for performing analytical operations such as groupby and aggregation."

    FIELD_DESCRIPTIONS = {
        "data": "Input DataFrame to analyze.",
        "groupby_cols": "Columns used for grouping the data.",
        "agg_functions": "Aggregation functions to apply to grouped data.",
        "sort_by": "Columns used to sort the resulting aggregated data.",
    }

    def __init__(
        self,
        data: Optional[DataFrame] = None,
        groupby_cols: Optional[List[str]] = None,
        agg_functions: Optional[Dict[str, str]] = None,
        sort_by: Optional[List[str]] = None,
    ) -> None:
        super().__init__(style="analysis", data=data)
        self.groupby_cols = groupby_cols if groupby_cols else []
        self.agg_functions = agg_functions if agg_functions else {}
        self.sort_by = sort_by if sort_by else []


TRANSFORM_PARAMS_CLASSES: Dict[str, Type[TransformParams]] = {
    "ml": MLTransformParams,
    "report": ReportTransformParams,
    "analysis": AnalysisTransformParams,
}
