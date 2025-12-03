"""
Extract Functions.
"""

from pathlib import Path
from typing import Dict, Any, Type
import pandas as pd
from sqlalchemy import create_engine
import requests
from requests.auth import HTTPBasicAuth


from fragua.extract.params import (
    CSVExtractParamsT,
    ExcelExtractParamsT,
    SQLExtractParamsT,
    APIExtractParamsT,
)

from fragua.extract.functions import ExtractFunction
from fragua.extract.params.base import ExtractParams


class CSVExtractFunction(ExtractFunction[CSVExtractParamsT]):
    """
    ExtractFunction for CSV files.
    """

    def __init__(self, name: str, params: CSVExtractParamsT) -> None:
        super().__init__(name=name, params=params)

    def summary(self) -> Dict[str, Any]:
        return {
            "function": self.name,
            "params_type": "CSVExtractParams",
            "purpose": "Extract tabular data from a CSV file",
        }

    def execute(self) -> pd.DataFrame:
        path: Path = self.params.path
        if not path:
            raise ValueError("'path' is required in params")

        read_kwargs = getattr(self.params, "read_kwargs", {}) or {}
        path_str = str(path) if isinstance(path, Path) else path
        return pd.read_csv(path_str, **read_kwargs)


class ExcelExtractFunction(ExtractFunction[ExcelExtractParamsT]):
    """
    ExtractFunction for Excel files.
    """

    def __init__(self, name: str, params: ExcelExtractParamsT) -> None:
        super().__init__(name=name, params=params)

    def summary(self) -> Dict[str, Any]:
        return {
            "function": self.name,
            "params_type": "ExcelExtractParams",
            "purpose": "Extract data from an Excel spreadsheet",
        }

    def execute(self) -> pd.DataFrame:
        path = self.params.path
        if not path:
            raise ValueError("'path' is required in params")

        read_kwargs = self.params.read_kwargs or {}
        path_str = str(path) if isinstance(path, Path) else path
        return pd.read_excel(path_str, sheet_name=self.params.sheet_name, **read_kwargs)


class SQLExtractFunction(ExtractFunction[SQLExtractParamsT]):
    """
    ExtractFunction for SQL databases.
    """

    def __init__(self, name: str, params: SQLExtractParamsT) -> None:
        super().__init__(name=name, params=params)

    def summary(self) -> Dict[str, Any]:
        return {
            "function": self.name,
            "params_type": "SQLExtractParams",
            "purpose": "Run a SQL query and extract the result as a DataFrame",
        }

    def execute(self) -> pd.DataFrame:
        connection_string = self.params.connection_string
        query = self.params.query
        if not connection_string or not query:
            raise ValueError("'connection_string' and 'query' are required in params")

        read_kwargs = self.params.read_kwargs or {}
        engine = create_engine(connection_string)
        try:
            with engine.connect() as conn:
                return pd.read_sql_query(query, conn, **read_kwargs)
        finally:
            engine.dispose()


class APIExtractFunction(ExtractFunction[APIExtractParamsT]):
    """
    ExtractFunction for REST APIs.
    """

    def __init__(self, name: str, params: APIExtractParamsT) -> None:
        super().__init__(name=name, params=params)

    def summary(self) -> Dict[str, Any]:
        return {
            "function": self.name,
            "params_type": "APIExtractParams",
            "purpose": "Fetch JSON data from a REST API",
        }

    def execute(self) -> pd.DataFrame:
        url = self.params.url
        if not url:
            raise ValueError("'url' is required in params")

        response = requests.request(
            method=self.params.method.upper(),
            url=url,
            headers=self.params.headers,
            params=self.params.params,
            data=self.params.data,
            auth=HTTPBasicAuth(**self.params.auth) if self.params.auth else None,
            proxies=self.params.proxy,
            timeout=self.params.timeout,
        )
        response.raise_for_status()

        result_data = response.json()
        read_kwargs = self.params.read_kwargs or {}

        if isinstance(result_data, list):
            return pd.DataFrame(result_data, **read_kwargs)
        if isinstance(result_data, dict):
            return pd.json_normalize(result_data, **read_kwargs)

        raise ValueError(f"Unexpected API response type: {type(result_data)}")


EXTRACT_FUNCTION_CLASSES: Dict[str, Type[ExtractFunction[ExtractParams]]] = {
    "csv": CSVExtractFunction,
    "excel": ExcelExtractFunction,
    "sql": SQLExtractFunction,
    "api": APIExtractFunction,
}
