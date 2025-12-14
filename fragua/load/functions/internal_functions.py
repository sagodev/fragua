"""
Internal helper functions for LoadFunction implementations.

These utilities encapsulate reusable logic commonly required
by load styles, such as validation, path resolution, data
normalization, and persistence operations.
"""

import os
from typing import Any, Callable, Dict
import pandas as pd

from fragua.load.params.load_params import ExcelLoadParams


def validate_excel_params(params: ExcelLoadParams) -> None:
    """
    Validate required parameters for Excel load operations.

    Ensures that:
    - the provided data is a pandas DataFrame
    - a destination directory has been defined

    Args:
        params (ExcelLoadParams): Load parameters for Excel output.

    Raises:
        TypeError: If `params.data` is not a pandas DataFrame.
        ValueError: If `params.destination` is missing or empty.
    """
    if not isinstance(params.data, pd.DataFrame):
        raise TypeError("ExcelLoadStyle requires a pandas DataFrame")
    if not params.destination:
        raise ValueError("Destination folder is required")


def build_excel_path(params: ExcelLoadParams) -> str:
    """
    Resolve and create the full filesystem path for an Excel output file.

    This function:
    - ensures the destination directory exists
    - appends the `.xlsx` extension if missing from the file name

    Args:
        params (ExcelLoadParams): Parameters containing destination and file name.

    Returns:
        str: Absolute or relative path to the Excel file.

    Raises:
        ValueError: If destination or file_name is not provided.
    """
    if params.destination is None:
        raise ValueError("'destination' must be provided")

    os.makedirs(params.destination, exist_ok=True)

    if params.file_name is None:
        raise ValueError("'file_name' must be provided")

    _, ext = os.path.splitext(params.file_name)
    file_name = params.file_name if ext else f"{params.file_name}.xlsx"

    return os.path.join(params.destination, file_name)


def convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert timezone-aware datetime columns to naive datetime.

    This normalization step avoids compatibility issues when
    exporting DataFrames to formats that do not support timezones
    (e.g., Excel).

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: A copy of the DataFrame with timezone-naive
        datetime columns.
    """
    datetime_cols = df.select_dtypes(include=["datetimetz"]).columns
    if len(datetime_cols) > 0:
        df = df.copy()
        for col in datetime_cols:
            df[col] = df[col].dt.tz_convert(None)
    return df


def write_excel(df: pd.DataFrame, path: str, sheet_name: str, index: bool) -> None:
    """
    Write a DataFrame to an Excel file.

    If the file already exists, the DataFrame is appended
    as a new sheet. Otherwise, a new file is created.

    Args:
        df (pd.DataFrame): DataFrame to persist.
        path (str): Full path to the Excel file.
        sheet_name (str): Target worksheet name.
        index (bool): Whether to include the DataFrame index.
    """
    if os.path.exists(path):
        with pd.ExcelWriter(
            path, mode="a", engine="openpyxl", if_sheet_exists="new"
        ) as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=index)
    else:
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=index)


LOAD_INTERNAL_FUNCTIONS: Dict[str, Callable[..., Any]] = {
    "validate_excel_params": validate_excel_params,
    "build_excel_path": build_excel_path,
    "convert_datetime_columns": convert_datetime_columns,
    "write_excel": write_excel,
}
