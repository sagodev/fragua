"""
Reusable Load Functions.
"""

import os
from typing import Any
import pandas as pd
import requests
from sqlalchemy import create_engine


from fragua.functions.function import FraguaFunction
from fragua.params.load_params import (
    ExcelLoadParams,
    LoadParams,
    SQLLoadParams,
    APILoadParams,
)
from fragua.params.params import Params


# ----------------------------- #
# --- Excel Helpers --- #
# ----------------------------- #


def validate_excel_params(params: ExcelLoadParams) -> None:
    """
    Validate Excel Load parameters.

    Args:
        params (ExcelLoadParams): Parameters for Excel Load.

    Raises:
        TypeError: If data is not a DataFrame.
        ValueError: If destination folder is missing.
    """
    if not isinstance(params.data, pd.DataFrame):
        raise TypeError("ExcelLoadStyle requires a pandas DataFrame")
    if not params.destination:
        raise ValueError("Destination folder is required")


def build_excel_path(params: ExcelLoadParams) -> str:
    """
    Build the full path for the Excel file, adding '.xlsx' if missing.

    Args:
        params (ExcelLoadParams): Parameters including destination and file_name.

    Returns:
        str: Full path to the Excel file.
    """
    os.makedirs(params.destination, exist_ok=True)

    _, ext = os.path.splitext(params.file_name)
    file_name = params.file_name if ext else f"{params.file_name}.xlsx"

    return os.path.join(params.destination, file_name)


def convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert timezone-aware datetime columns to naive datetime.

    Args:
        df (pd.DataFrame): DataFrame to process.

    Returns:
        pd.DataFrame: DataFrame with naive datetime columns.
    """
    datetime_cols = df.select_dtypes(include=["datetimetz"]).columns
    if len(datetime_cols) > 0:
        df = df.copy()
        for col in datetime_cols:
            df[col] = df[col].dt.tz_convert(None)
    return df


def write_excel(df: pd.DataFrame, path: str, sheet_name: str, index: bool) -> None:
    """
    Write or append a DataFrame to an Excel file.

    Args:
        df (pd.DataFrame): DataFrame to write.
        path (str): Full path to Excel file.
        sheet_name (str): Sheet name to write to.
        index (bool): Whether to write the index.
    """
    if os.path.exists(path):
        with pd.ExcelWriter(
            path, mode="a", engine="openpyxl", if_sheet_exists="new"
        ) as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=index)
    else:
        with pd.ExcelWriter(path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=index)


# ----------------------------- #
# --- SQL Helpers --- #
# ----------------------------- #


def validate_sql_params(params: SQLLoadParams) -> None:
    """
    Validate SQL Load parameters.

    Args:
        params (SQLLoadParams): Parameters for SQL Load.

    Raises:
        TypeError: If data is not a DataFrame.
        ValueError: If destination or table_name is missing.
    """
    if not isinstance(params.data, pd.DataFrame):
        raise TypeError("SQLLoadStyle requires a pandas DataFrame")
    if not params.destination:
        raise ValueError("destination (connection_string) is required")
    if not params.table_name:
        raise ValueError("table_name is required")


def write_sql(params: SQLLoadParams) -> pd.DataFrame:
    """
    Write a DataFrame to a SQL table.

    Args:
        params (SQLLoadParams): Parameters including data and table information.

    Returns:
        pd.DataFrame: Delivered DataFrame.
    """
    engine = create_engine(params.destination)
    try:
        params.data.to_sql(
            name=params.table_name,
            con=engine,
            if_exists=params.if_exists,
            index=params.index,
            chunksize=params.chunksize,
        )
    finally:
        engine.dispose()
    return params.data


# ----------------------------- #
# --- API Helpers --- #
# ----------------------------- #


def validate_api_params(params: APILoadParams) -> None:
    """
    Validate API Load parameters.

    Args:
        params (APILoadParams): Parameters for API Load.

    Raises:
        ValueError: If data or endpoint is missing.
    """
    if params.data is None:
        raise ValueError("data is required")
    if not params.endpoint:
        raise ValueError("endpoint is required")


def send_api_request(params: APILoadParams) -> Any:
    """
    Send a REST API request with the provided data.

    Args:
        params (APILoadParams): Parameters including endpoint, method, headers, and data.

    Returns:
        Any: The delivered data.
    """
    headers: dict[Any, Any] = params.headers or {}
    if params.auth:
        token = params.auth.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"

    response = requests.request(
        method=params.method,
        url=params.endpoint,
        json=params.data,
        headers=headers,
        timeout=params.timeout,
    )
    response.raise_for_status()
    return params.data


# ----------------------------- #
# --- Pipelines --- #
# ----------------------------- #


class LoadFunction(FraguaFunction, Params):
    """
    Represents a Load function in the Fragua framework.
    """

    def __init__(self, name: str, params: LoadParams) -> None:
        super().__init__(name=name, action="load", params=params)


class APILoadFunction(LoadFunction):
    """
    LoadFunction for API pipelines.
    """

    def __init__(self, name: str, params: APILoadParams) -> None:
        super().__init__(name=name, params=params)

    def execute(self) -> Any:
        validate_api_params(self.params)
        return send_api_request(self.params)


class SQLLoadFunction(LoadFunction):
    """
    LoadFunction for SQL pipelines.
    """

    def __init__(self, name: str, params: SQLLoadParams) -> None:
        super().__init__(name=name, params=params)

    def execute(self) -> pd.DataFrame:
        validate_sql_params(self.params)
        return write_sql(self.params)


class ExcelLoadFunction(LoadFunction):
    """
    LoadFunction for Excel pipelines.
    """

    def __init__(self, name: str, params: ExcelLoadParams) -> None:
        super().__init__(name=name, params=params)

    def execute(self) -> pd.DataFrame:
        validate_excel_params(self.params)
        path = build_excel_path(self.params)
        df = convert_datetime_columns(self.params.data)
        write_excel(df, path, self.params.sheet_name or "Sheet1", self.params.index)
        return df
