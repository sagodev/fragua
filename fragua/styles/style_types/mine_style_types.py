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
    CSVMineParamsT,
    ExcelMineParamsT,
    SQLMineParamsT,
    APIMineParamsT,
)


# ---------------------------------------------------------------------- #
# CSV Extraction
# ---------------------------------------------------------------------- #
@register_mine_style("csv")
class CSVMineStyle(MineStyle[CSVMineParamsT, DataFrame]):
    """Extracts data from CSV files."""

    def extract(self, params: CSVMineParamsT) -> DataFrame:
        path = params.path
        if not path:
            raise ValueError(f"{self.style_name}: 'path' is required in params")

        read_kwargs = params.read_kwargs or {}

        path_str = str(path) if isinstance(path, Path) else path
        return pd.read_csv(path_str, **read_kwargs)


# ---------------------------------------------------------------------- #
# Excel Extraction
# ---------------------------------------------------------------------- #
@register_mine_style("excel")
class ExcelMineStyle(MineStyle[ExcelMineParamsT, DataFrame]):
    """Extracts data from Excel files."""

    def extract(self, params: ExcelMineParamsT) -> DataFrame:
        path = params.path
        if not path:
            raise ValueError(f"{self.style_name}: 'path' is required in params")

        sheet_name = params.sheet_name
        read_kwargs = params.read_kwargs or {}

        path_str = str(path) if isinstance(path, Path) else path
        return pd.read_excel(path_str, sheet_name=sheet_name, **read_kwargs)


# ---------------------------------------------------------------------- #
# SQL Extraction
# ---------------------------------------------------------------------- #
@register_mine_style("sql")
class SQLMineStyle(MineStyle[SQLMineParamsT, DataFrame]):
    """Extracts data from SQL databases."""

    def extract(self, params: SQLMineParamsT) -> DataFrame:
        connection_string = params.connection_string
        query = params.query
        if not connection_string or not query:
            raise ValueError(
                f"{self.style_name}: 'connection_string' and 'query' are required in params"
            )

        read_kwargs = params.read_kwargs or {}

        engine = create_engine(connection_string)
        try:
            with engine.connect() as conn:
                return pd.read_sql_query(query, conn, **read_kwargs)
        finally:
            engine.dispose()


# ---------------------------------------------------------------------- #
# API Extraction
# ---------------------------------------------------------------------- #
@register_mine_style("api")
class APIMineStyle(MineStyle[APIMineParamsT, DataFrame]):
    """Extracts data from REST APIs."""

    def extract(self, params: APIMineParamsT) -> DataFrame:
        url = params.url
        if not url:
            raise ValueError(f"{self.style_name}: 'url' is required in params")

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

        read_kwargs = params.read_kwargs or {}
        if isinstance(result_data, list):
            return pd.DataFrame(result_data, **read_kwargs)
        if isinstance(result_data, dict):
            return pd.json_normalize(result_data, **read_kwargs)

        raise ValueError(
            f"{self.style_name}: Unexpected API response type: {type(result_data)}"
        )
