"""
Forge parameters classes for different types of data transformations.
"""

from typing import Any, Dict, TypeVar
from pandas import DataFrame
from fragua.core.base_params import BaseParams, register_params


class ForgeParams(BaseParams):
    """Common parameters for forge (transformation) agents."""

    data: DataFrame


agent: str = "blacksmith"


@register_params(agent, style="ml")
class MLForgeParams(ForgeParams):
    """Parameters for machine learning transformations."""

    target_column: str | None = None
    categorical_cols: list[str] | None = None
    numeric_cols: list[str] | None = None
    outlier_threshold: float | None = None


@register_params(agent, style="report")
class ReportForgeParams(ForgeParams):
    """Parameters for report generation transformations."""

    format_config: Dict[str, Any] | None = None
    derived_columns: Dict[str, str] | None = None
    rounding_precision: int | None = None


@register_params(agent, style="analysis")
class AnalysisForgeParams(ForgeParams):
    """Parameters for data analysis transformations."""

    groupby_cols: list[str] | None = None
    agg_functions: Dict[str, str] | None = None
    sort_by: list[str] | None = None


ForgeParamsT = TypeVar("ForgeParamsT", bound=ForgeParams)
MLForgeParamsT = TypeVar("MLForgeParamsT", bound=MLForgeParams)
ReportForgeParamsT = TypeVar("ReportForgeParamsT", bound=ReportForgeParams)
AnalysisForgeParamsT = TypeVar("AnalysisForgeParamsT", bound=AnalysisForgeParams)
