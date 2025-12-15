"""
Transform parameter classes for different transformation pipelines.

Each class defines the configuration schema required by a specific
TransformFunction and TransformStyle, encapsulating both the input
DataFrame and transformation-specific options.
"""

from typing import Any, Dict, List, Optional, Type
from pandas import DataFrame
from fragua.transform.params.base import TransformParams

# pylint: disable=too-many-arguments, too-many-positional-arguments
# pylint: disable=too-few-public-methods


class MLTransformParams(TransformParams):
    """
    Parameters for machine learning transformation pipelines.

    These parameters define how raw datasets should be prepared
    for ML workflows, including handling of categorical and numeric
    features, target definition, and outlier treatment.
    """

    purpose = (
        "Transformation parameters used to prepare data for machine learning tasks."
    )

    FIELD_DESCRIPTIONS = {
        "data": "Input DataFrame containing the dataset.",
        "target_column": "Name of the target variable to be predicted.",
        "categorical_cols": "List of columns treated as categorical features.",
        "numeric_cols": "List of columns treated as numeric features.",
        "outlier_threshold": "Threshold factor used for outlier detection or capping.",
    }

    def __init__(
        self,
        data: Optional[DataFrame] = None,
        target_column: Optional[str] = None,
        categorical_cols: Optional[List[str]] = None,
        numeric_cols: Optional[List[str]] = None,
        outlier_threshold: Optional[float] = None,
    ) -> None:
        """
        Initialize ML transformation parameters.

        Args:
            data (Optional[DataFrame]):
                Input dataset to be transformed.
            target_column (Optional[str]):
                Name of the dependent variable for modeling.
            categorical_cols (Optional[List[str]]):
                Columns to be treated as categorical features.
            numeric_cols (Optional[List[str]]):
                Columns to be treated as numeric features.
            outlier_threshold (Optional[float]):
                Threshold factor used in outlier handling logic.
        """
        super().__init__(style="ml", data=data)
        self.target_column = target_column if target_column else ""
        self.categorical_cols = categorical_cols if categorical_cols else []
        self.numeric_cols = numeric_cols if numeric_cols else []
        self.outlier_threshold = outlier_threshold


class ReportTransformParams(TransformParams):
    """
    Parameters for report-oriented transformation pipelines.

    These parameters focus on formatting, derived metrics,
    and presentation-ready transformations.
    """

    purpose = (
        "Parameters used to prepare, derive, and format data for reporting purposes."
    )

    FIELD_DESCRIPTIONS = {
        "data": "Input DataFrame prior to formatting and enrichment.",
        "format_config": "Formatting rules such as styles or alignment.",
        "derived_columns": "Computed columns defined via expressions.",
        "rounding_precision": "Decimal precision applied to numeric values.",
    }

    def __init__(
        self,
        data: Optional[DataFrame] = None,
        format_config: Optional[Dict[str, Any]] = None,
        derived_columns: Optional[Dict[str, str]] = None,
        rounding_precision: Optional[int] = None,
    ) -> None:
        """
        Initialize report transformation parameters.

        Args:
            data (Optional[DataFrame]):
                Input dataset to be formatted.
            format_config (Optional[Dict[str, Any]]):
                Configuration for output formatting rules.
            derived_columns (Optional[Dict[str, str]]):
                Mapping of new column names to expression definitions.
            rounding_precision (Optional[int]):
                Number of decimal places for numeric rounding.
        """
        super().__init__(style="report", data=data)
        self.format_config = format_config if format_config else {}
        self.derived_columns = derived_columns if derived_columns else {}
        self.rounding_precision = rounding_precision if rounding_precision else 2


class AnalysisTransformParams(TransformParams):
    """
    Parameters for analytical transformation pipelines.

    These parameters enable grouping, aggregation, and sorting
    operations commonly used in exploratory data analysis.
    """

    purpose = (
        "Parameters for performing analytical operations such as "
        "grouping, aggregation, and sorting."
    )

    FIELD_DESCRIPTIONS = {
        "data": "Input DataFrame to be analyzed.",
        "groupby_cols": "Columns used to group the data.",
        "agg_functions": "Aggregation functions applied per column.",
        "sort_by": "Columns used to sort the final result.",
    }

    def __init__(
        self,
        data: Optional[DataFrame] = None,
        groupby_cols: Optional[List[str]] = None,
        agg_functions: Optional[Dict[str, str]] = None,
        sort_by: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize analysis transformation parameters.

        Args:
            data (Optional[DataFrame]):
                Input dataset to analyze.
            groupby_cols (Optional[List[str]]):
                Columns used for grouping operations.
            agg_functions (Optional[Dict[str, str]]):
                Aggregation functions mapped per column.
            sort_by (Optional[List[str]]):
                Columns used to sort aggregated results.
        """
        super().__init__(style="analysis", data=data)
        self.groupby_cols = groupby_cols if groupby_cols else []
        self.agg_functions = agg_functions if agg_functions else {}
        self.sort_by = sort_by if sort_by else []


TRANSFORM_PARAMS_CLASSES: Dict[str, Type[TransformParams]] = {
    "ml": MLTransformParams,
    "report": ReportTransformParams,
    "analysis": AnalysisTransformParams,
}
