"""
Concrete extraction function implementations.

This module provides ExtractFunction implementations for common
data sources such as CSV files, Excel spreadsheets, SQL databases,
and REST APIs.
"""

from pathlib import Path
from typing import Dict, Any, Type
import pandas as pd
from sqlalchemy import create_engine
import requests
from requests.auth import HTTPBasicAuth


from fragua.core.function import FraguaFunction
from fragua.extract.params.extract_params import (
    APIExtractParams,
    CSVExtractParams,
    ExcelExtractParams,
    SQLExtractParams,
)


class CSVExtractFunction(FraguaFunction[CSVExtractParams]):
    """
    Extract data from a CSV file.
    """

    action = "extract"
    params_type = CSVExtractParams
    purpose = "Extract tabular data from a CSV file."

    def execute(
        self,
        input_data: None,
        params: CSVExtractParams,
        context: Any,
    ) -> pd.DataFrame:
        path = params.get("path")
        if not path:
            raise ValueError("'path' is required in params")

        return pd.read_csv(str(Path(path)))


class ExcelExtractFunction(FraguaFunction[ExcelExtractParams]):
    """
    Extract data from an Excel file.
    """

    action = "extract"
    params_type = ExcelExtractParams
    purpose = "Extract data from an Excel spreadsheet."

    def execute(
        self,
        input_data: None,
        params: ExcelExtractParams,
        context: Any,
    ) -> pd.DataFrame:
        path = params.get("path")
        if not path:
            raise ValueError("'path' is required in params")

        return pd.read_excel(
            str(Path(path)),
            sheet_name=params.get("sheet_name"),
        )


class SQLExtractFunction(FraguaFunction[SQLExtractParams]):
    """
    Execute a SQL query and return the result as a DataFrame.
    """

    action = "extract"
    params_type = SQLExtractParams
    purpose = "Execute a SQL query and extract the result as a DataFrame."

    def execute(
        self,
        input_data: None,
        params: SQLExtractParams,
        context: Any,
    ) -> pd.DataFrame:
        connection_string = params.get("connection_string")
        query = params.get("query")

        if not connection_string or not query:
            raise ValueError("'connection_string' and 'query' are required in params")

        engine = create_engine(connection_string)
        try:
            with engine.connect() as conn:
                return pd.read_sql_query(query, conn)
        finally:
            engine.dispose()


class APIExtractFunction(FraguaFunction[APIExtractParams]):
    """
    Fetch JSON data from a REST API.
    """

    action = "extract"
    params_type = APIExtractParams
    purpose = "Fetch JSON data from a REST API endpoint."

    def execute(
        self,
        input_data: None,
        params: APIExtractParams,
        context: Any,
    ) -> pd.DataFrame:
        url = params.get("url")
        if not url:
            raise ValueError("'url' is required in params")

        response = requests.request(
            method=params.get("method"),
            url=url,
            headers=params.get("headers"),
            params=params.get("params"),
            data=params.get("data"),
            auth=HTTPBasicAuth(**params.get("auth")) if params.get("auth") else None,
            proxies=params.get("proxy"),
            timeout=params.get("timeout"),
        )
        response.raise_for_status()

        payload = response.json()

        if isinstance(payload, list):
            return pd.DataFrame(payload)

        if isinstance(payload, dict):
            return pd.json_normalize(payload)

        raise ValueError(f"Unexpected API response type: {type(payload)}")


EXTRACT_FUNCTION_CLASSES: Dict[str, Type[FraguaFunction]] = {
    "csv": CSVExtractFunction,
    "excel": ExcelExtractFunction,
    "sql": SQLExtractFunction,
    "api": APIExtractFunction,
}
