"""
Load function implementations.

This module defines concrete LoadFunction classes responsible
for persisting processed data into external destinations.
Each function encapsulates the low-level persistence logic
for a specific target system or format.
"""

from typing import Any, Dict, Type
import pandas as pd

from fragua.core.function import FraguaFunction
from fragua.core.params import FraguaParamsT
from fragua.load.functions.internal_functions import LOAD_INTERNAL_FUNCTIONS
from fragua.load.params.load_params import (
    APILoadParams,
    CSVLoadParams,
    ExcelLoadParams,
    SQLLoadParams,
)


class LoadPipeline(FraguaFunction[FraguaParamsT]):
    """
    Base class for load pipelines executed as ordered internal steps.

    A load pipeline orchestrates persistence-related operations
    such as validation, path resolution, normalization and output writing.
    """

    action = "load"

    def execute(
        self,
        input_data: pd.DataFrame,
        params: FraguaParamsT,
        context: Any = None,
    ) -> pd.DataFrame:
        """
        Execute the load pipeline.

        Args:
            input_data:
                DataFrame to be persisted.
            params:
                Configuration object containing load options.
            context:
                Optional execution context (reserved for future use).

        Returns:
            pd.DataFrame:
                The persisted DataFrame.

        Raises:
            KeyError:
                If a load step is not registered.
        """
        data = input_data
        artifacts: dict[str, Any] = {}

        for step in self.steps or ():
            if step not in LOAD_INTERNAL_FUNCTIONS:
                raise KeyError(f"Load function '{step}' not registered.")

            spec = LOAD_INTERNAL_FUNCTIONS[step]

            kwargs = {
                key: getattr(params, key)
                for key in spec.config_keys
                if hasattr(params, key)
            }

            result = spec.func(data=data, **kwargs)

            if isinstance(result, pd.DataFrame):
                data = result
            elif isinstance(result, dict):
                artifacts.update(result)

        return data


class ExcelLoadFunction(LoadPipeline[ExcelLoadParams]):
    """
    Load pipeline for exporting DataFrames to Excel files.
    """

    action = "load"
    params_type = ExcelLoadParams
    purpose = "Export a DataFrame to an Excel file."

    steps = [
        "validate_load",
        "build_path",
        "convert_datetime_columns",
        "write_excel",
    ]


class CSVLoadFunction(LoadPipeline[CSVLoadParams]):
    """
    Load pipeline for exporting DataFrames to CSV files.
    """

    action = "load"
    params_type = CSVLoadParams
    purpose = "Export a DataFrame to a CSV file."

    steps = [
        "validate_load",
        "build_path",
        "write_csv",
    ]


class SQLLoadFunction(LoadPipeline[SQLLoadParams]):
    """
    Load pipeline for SQL database outputs.
    """

    action = "load"
    params_type = SQLLoadParams
    purpose = "Persist a DataFrame into a SQL database table."

    internal_functions = LOAD_INTERNAL_FUNCTIONS

    steps = [
        "validate_sql_load",
        "write_sql",
    ]


class APILoadFunction(LoadPipeline[APILoadParams]):
    """Load pipeline for API database outputs."""

    action = "load"
    params_type = APILoadParams
    purpose = "Parameters required to send data to an external API."
    steps = [
        "validate_api_load",
        "write_api",
    ]


LOAD_FUNCTION_CLASSES: Dict[str, Type[FraguaFunction]] = {
    "excel": ExcelLoadFunction,
    "csv": CSVLoadFunction,
    "sql": SQLLoadFunction,
    "api": APILoadFunction,
}
