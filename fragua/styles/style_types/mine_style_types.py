"""
MineStyle types for various data extraction methods.
"""

from pathlib import Path
from sqlalchemy import create_engine
from pandas import DataFrame
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

from fragua.styles.mine_style import MineStyle, register_mine_style
from fragua.params.mine_params import (
    CSVMineParams,
    ExcelMineParams,
    SQLMineParams,
    APIMineParams,
)


@register_mine_style("csv")
class CSVMineStyle(MineStyle[CSVMineParams, DataFrame]):
    """Extracts data from CSV files."""

    def extract(self, source_params: CSVMineParams) -> DataFrame:
        path = source_params.path
        if not path:
            raise ValueError("path is required in source_params")

        read_kwargs = source_params.read_kwargs

        path_str = str(path) if isinstance(path, Path) else path
        return pd.read_csv(path_str, **read_kwargs)


@register_mine_style("excel")
class ExcelMineStyle(MineStyle[ExcelMineParams, DataFrame]):
    """Extracts data from Excel files."""

    def extract(self, source_params: ExcelMineParams) -> DataFrame:
        path = source_params.path
        if not path:
            raise ValueError("path is required in source_params")

        sheet_name = source_params.sheet_name
        read_kwargs = source_params.read_kwargs

        path_str = str(path) if isinstance(path, Path) else path
        return pd.read_excel(path_str, sheet_name=sheet_name, **read_kwargs)


@register_mine_style("sql")
class SQLMineStyle(MineStyle[SQLMineParams, DataFrame]):
    """Extracts data from SQL databases."""

    def extract(self, source_params: SQLMineParams) -> DataFrame:
        """Extract data from a SQL database."""
        connection_string = source_params.connection_string
        query = source_params.query
        if not connection_string or not query:
            raise ValueError(
                "connection_string and query are required in source_params"
            )

        read_kwargs = source_params.read_kwargs

        engine = create_engine(connection_string)
        try:
            with engine.connect() as conn:
                return pd.read_sql_query(query, conn, **read_kwargs)
        finally:
            engine.dispose()


@register_mine_style("api")
class APIMineStyle(MineStyle[APIMineParams, DataFrame]):
    """Extracts data from REST APIs."""

    def extract(self, source_params: APIMineParams) -> DataFrame:
        """Extract data from a REST API endpoint."""
        url = source_params.url
        if not url:
            raise ValueError("url is required in source_params")

        response = requests.request(
            method=source_params.method.upper(),
            url=url,
            headers=source_params.headers,
            params=source_params.params,
            data=source_params.data,
            auth=HTTPBasicAuth(**source_params.auth) if source_params.auth else None,
            proxies=source_params.proxy,
            timeout=source_params.timeout,
        )
        response.raise_for_status()
        result_data = response.json()

        read_kwargs = source_params.read_kwargs
        if isinstance(result_data, list):
            return pd.DataFrame(result_data, **read_kwargs)
        if isinstance(result_data, dict):
            return pd.json_normalize(result_data, **read_kwargs)

        raise ValueError(f"Unexpected API response type: {type(result_data)}")
