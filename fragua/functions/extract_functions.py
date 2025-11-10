"""
Reusable Extract Functions.
"""

from typing import Any
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
import requests
from requests.auth import HTTPBasicAuth

from fragua.functions.function_registry import register_function
from fragua.params.extract_params import (
    CSVExtractParams,
    ExcelExtractParams,
    SQLExtractParams,
    APIExtractParams,
)

action: str = "extract"


@register_function(action, "extract_csv")
def extract_csv(params: CSVExtractParams) -> pd.DataFrame:
    """Extract data from CSV file."""
    path = params.path
    if not path:
        raise ValueError("'path' is required in params")

    read_kwargs: dict[Any, Any] = params.read_kwargs or {}
    path_str = str(path) if isinstance(path, Path) else path
    return pd.read_csv(path_str, **read_kwargs)


@register_function(action, "extract_excel")
def extract_excel(params: ExcelExtractParams) -> pd.DataFrame:
    """Extract data from Excel file."""
    path = params.path
    if not path:
        raise ValueError("'path' is required in params")

    read_kwargs: dict[Any, Any] = params.read_kwargs or {}
    path_str = str(path) if isinstance(path, Path) else path
    return pd.read_excel(path_str, sheet_name=params.sheet_name, **read_kwargs)


@register_function(action, "extract_sql")
def extract_sql(params: SQLExtractParams) -> pd.DataFrame:
    """Extract data from SQL database."""
    connection_string = params.connection_string
    query = params.query
    if not connection_string or not query:
        raise ValueError("'connection_string' and 'query' are required in params")

    read_kwargs: dict[Any, Any] = params.read_kwargs or {}
    engine = create_engine(connection_string)
    try:
        with engine.connect() as conn:
            return pd.read_sql_query(query, conn, **read_kwargs)
    finally:
        engine.dispose()


@register_function(action, "extract_api")
def extract_api(params: APIExtractParams) -> pd.DataFrame:
    """Extract data from REST API."""
    url = params.url
    if not url:
        raise ValueError("'url' is required in params")

    response = requests.request(
        method=params.method.upper(),
        url=url,
        headers=params.headers,
        params=params.params,
        data=params.data,
        auth=HTTPBasicAuth(**params.auth) if params.auth else None,
        proxies=params.proxy,
        timeout=params.timeout,
    )
    response.raise_for_status()

    result_data = response.json()
    read_kwargs: dict[Any, Any] = params.read_kwargs or {}
    if isinstance(result_data, list):
        return pd.DataFrame(result_data, **read_kwargs)
    if isinstance(result_data, dict):
        return pd.json_normalize(result_data, **read_kwargs)

    raise ValueError(f"Unexpected API response type: {type(result_data)}")
