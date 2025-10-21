"""
Concrete ExtractionStyle classes with dynamic registration for Fragua ETL.
"""

from typing import Any, Dict
from pathlib import Path
from sqlalchemy import create_engine
from pandas import DataFrame
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

from fragua.styles.extraction_style import (
    ExtractionStyle,
    register_extraction_style,
)


@register_extraction_style("csv")
class CSVExtractionStyle(ExtractionStyle[Any, Any]):
    """Extracts data from CSV files."""

    def __init__(self, style_name: str) -> None:
        super().__init__(style_name=style_name)

    def extract(self, source_params: Dict[str, Any]) -> DataFrame:
        """Extract data from a CSV file.

        Args:
            source_params: Dictionary containing CSV source parameters.

        Returns:
            DataFrame: The extracted data

        Raises:
            ValueError: If path is missing or invalid
            pd.errors.EmptyDataError: If CSV file is empty
            IOError: If file cannot be opened/read
        """
        # Input validation
        path = source_params["path"]
        if not path:
            raise ValueError("path is required in source_params")

        # Extract with optional parameters
        read_kwargs = source_params.get("read_kwargs", {})

        if isinstance(path, Path):
            path_str = str(path)
        else:
            path_str = path

        return pd.read_csv(path_str, **read_kwargs)


@register_extraction_style("excel")
class ExcelExtractionStyle(ExtractionStyle[Any, Any]):
    """Extracts data from Excel files."""

    def __init__(self, style_name: str) -> None:
        super().__init__(style_name=style_name)

    def extract(self, source_params: Dict[str, Any]) -> DataFrame:
        """Extract data from an Excel file.

        Args:
            source_params: Dictionary containing Excel source parameters.

        Returns:
            DataFrame: The extracted data

        Raises:
            ValueError: If path is missing or invalid
            pd.errors.EmptyDataError: If Excel file is empty
            IOError: If file cannot be opened/read
        """
        # Input validation
        path = source_params["path"]
        if not path:
            raise ValueError("path is required in source_params")

        # Extract with optional parameters
        sheet_name = source_params.get("sheet_name", 0)
        read_kwargs = source_params.get("read_kwargs", {})

        if isinstance(path, Path):
            path_str = str(path)
        else:
            path_str = path

        return pd.read_excel(path_str, sheet_name=sheet_name, **read_kwargs)


@register_extraction_style("sql")
class SQLExtractionStyle(ExtractionStyle[Any, Any]):
    """Extracts data from SQL databases."""

    def __init__(self, style_name: str) -> None:
        super().__init__(style_name=style_name)

    def extract(self, source_params: Dict[str, Any]) -> DataFrame:
        """Extract data from a SQL database.

        Args:
            source_params: Dictionary containing SQL source parameters.

        Returns:
            DataFrame: The extracted data

        Raises:
            ValueError: If connection string or query is missing
            RuntimeError: If SQLAlchemy is not installed
            SQLAlchemyError: If database connection fails
        """
        # Input validation
        connection_string = source_params["connection_string"]
        if not connection_string:
            raise ValueError("connection_string is required in source_params")

        query = source_params["query"]
        if not query:
            raise ValueError("query is required in source_params")

        # Extract with optional parameters
        read_kwargs = source_params.get("read_kwargs", {})

        engine = create_engine(connection_string)
        try:
            with engine.connect() as conn:
                df = pd.read_sql_query(query, conn, **read_kwargs)
                return df
        finally:
            engine.dispose()


@register_extraction_style("api")
class APIExtractionStyle(ExtractionStyle[Any, Any]):
    """Extracts data from REST APIs."""

    def __init__(self, style_name: str) -> None:
        super().__init__(style_name=style_name)

    def extract(self, source_params: Dict[str, Any]) -> DataFrame:
        """Extract data from a REST API endpoint.

        Args:
            source_params: Dictionary containing API source parameters.

        Returns:
            DataFrame: The extracted data

        Raises:
            ValueError: If URL is missing or response is not JSON
            RequestException: If API request fails
        """
        url = source_params["url"]
        if not url:
            raise ValueError("url is required in source_params")

        method = source_params.get("method", "GET").upper()
        headers = source_params.get("headers", {})
        params = source_params.get("params", None)
        data = source_params.get("data", None)
        auth = source_params.get("auth", None)
        proxy = source_params.get("proxy", None)
        timeout = source_params.get("timeout", 30.0)
        read_kwargs = source_params.get("read_kwargs", {})

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            auth=HTTPBasicAuth(**auth) if auth else None,
            proxies=proxy,
            timeout=timeout,
        )
        response.raise_for_status()
        result_data = response.json()

        if isinstance(result_data, list):
            return pd.DataFrame(result_data, **read_kwargs)
        if isinstance(result_data, dict):
            return pd.json_normalize(result_data, **read_kwargs)

        raise ValueError(f"Unexpected API response type: {type(result_data)}")
