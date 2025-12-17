"""
Transform style implementations for different data transformation scenarios.

Each TransformStyle defines how a specific category of transformations
(machine learning, reporting, or analysis) is executed by delegating
the operation to the appropriate TransformFunction and parameter type.
"""

from typing import Any, Dict, Type
import pandas as pd

from fragua.core.style import FraguaStyle
from fragua.transform.functions.transform_functions import (
    AnalysisTransformFunction,
    MLTransformFunction,
    ReportTransformFunction,
)


from fragua.transform.params.transform_params import (
    AnalysisTransformParams,
    MLTransformParams,
    ReportTransformParams,
)


class MLTransformStyle(FraguaStyle[MLTransformParams]):
    """
    Transform style dedicated to machine learning preprocessing workflows.

    Delegates the transformation logic to MLTransformFunction.
    """

    action = "transform"
    function = MLTransformFunction.__name__
    params_type = MLTransformParams.__name__
    purpose = "Apply machine learning preprocessing steps."

    def execute(
        self,
        params: MLTransformParams,
        input_data: pd.DataFrame | None = None,
        context: Any = None,
    ) -> pd.DataFrame:
        """
        Execute ML preprocessing transformation.

        Args:
            params (MLTransformParams): Parameters defining preprocessing configuration.
            input_data (pd.DataFrame | None): Input dataset.
            context (Any): Optional runtime context.

        Returns:
            pd.DataFrame: Transformed dataset ready for ML.
        """
        df = pd.DataFrame() if input_data is None else input_data

        return MLTransformFunction().execute(
            input_data=df, params=params, context=context
        )


class ReportTransformStyle(FraguaStyle[ReportTransformParams]):
    """
    Transform style focused on preparing data for reporting outputs.

    Delegates the transformation logic to ReportTransformFunction.
    """

    action = "transform"
    function = MLTransformFunction.__name__
    params_type = ReportTransformParams.__name__
    purpose = "Prepare data for reporting."

    def execute(
        self,
        params: ReportTransformParams,
        input_data: pd.DataFrame | None = None,
        context: Any = None,
    ) -> pd.DataFrame:
        """
        Execute reporting-oriented transformation.

        Args:
            params (ReportTransformParams): Parameters defining report transformation rules.
            input_data (pd.DataFrame | None): Input dataset.
            context (Any): Optional runtime context.

        Returns:
            pd.DataFrame: Dataset formatted for reporting.
        """
        df = pd.DataFrame() if input_data is None else input_data

        return ReportTransformFunction().execute(
            input_data=df, params=params, context=context
        )


class AnalysisTransformStyle(FraguaStyle[AnalysisTransformParams]):
    """
    Transform style for analytical data transformations.

    Delegates the transformation logic to AnalysisTransformFunction.
    """

    action = "transform"
    function = AnalysisTransformFunction.__name__
    params_type = AnalysisTransformParams.__name__
    purpose = "Perform analytical transformations."

    def execute(
        self,
        params: AnalysisTransformParams,
        input_data: pd.DataFrame | None = None,
        context: Any = None,
    ) -> pd.DataFrame:
        """
        Execute analysis-oriented transformation.

        Args:
            params (AnalysisTransformParams): Parameters defining analytical logic.
            input_data (pd.DataFrame | None): Input dataset.
            context (Any): Optional runtime context.

        Returns:
            pd.DataFrame: Dataset transformed for analytical purposes.
        """
        df = pd.DataFrame() if input_data is None else input_data

        return AnalysisTransformFunction().execute(
            input_data=df, params=params, context=context
        )


TRANSFORM_STYLE_CLASSES: Dict[str, Type[FraguaStyle]] = {
    "ml": MLTransformStyle,
    "report": ReportTransformStyle,
    "analysis": AnalysisTransformStyle,
}
