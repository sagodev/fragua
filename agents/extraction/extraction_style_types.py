"""
Concrete ExtractionStyle classes with dynamic registration for Fragua ETL.
"""

from typing import Optional, Dict, Any, Union, TypedDict, cast
import pandas as pd
from pandas import DataFrame
import requests

from agents.extraction.extraction_style import (
    ExtractionStyle,
    register_extraction_style,
)


class CSVSource(TypedDict, total=False):
    """Type definition for CSV source parameters."""

    path: str
    read_kwargs: Dict[str, Any]


class ExcelSource(TypedDict, total=False):
    """Type definition for Excel source parameters."""

    path: str
    sheet_name: Union[str, int]
    read_kwargs: Dict[str, Any]


class SQLSource(TypedDict, total=False):
    """Type definition for SQL source parameters."""

    connection_string: str
    query: str
    read_kwargs: Dict[str, Any]


class APISource(TypedDict, total=False):
    """Type definition for API source parameters."""

    endpoint: str
    method: str
    headers: Dict[str, str]
    params: Dict[str, str]
    timeout: float


# Source type definitions
class CSVSource(TypedDict):
    """Type definition for CSV source parameters."""

    path: str
    read_kwargs: Optional[Dict[str, Any]]


class ExcelSource(TypedDict):
    """Type definition for Excel source parameters."""

    path: str
    sheet_name: Optional[Union[str, int]]
    read_kwargs: Optional[Dict[str, Any]]


class SQLSource(TypedDict):
    """Type definition for SQL source parameters."""

    connection_string: str
    query: str
    read_kwargs: Optional[Dict[str, Any]]


class APISource(TypedDict):
    """Type definition for API source parameters."""

    endpoint: str
    params: Optional[Dict[str, Any]]
    headers: Optional[Dict[str, Any]]


@register_extraction_style("csv")
class CSVExtractionStyle(ExtractionStyle[DataFrame]):
    """Extracts data from CSV files."""

    def __init__(
        self, style_name: str, path: str, read_kwargs: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(style_name=style_name)
        self.path = path
        self.read_kwargs = read_kwargs or {}

    def extract(self, source: Optional[DataFrame] = None) -> DataFrame:
        """Extract data from a CSV file.

        Args:
            source: Not used in CSV extraction, here for interface compatibility.

        Returns:
            DataFrame: The extracted data.
        """
        # We ignore source since CSVExtractionStyle doesn't transform existing data
        df: DataFrame = pd.read_csv(self.path, **cast(Dict[str, Any], self.read_kwargs))
        return df


@register_extraction_style("excel")
class ExcelExtractionStyle(ExtractionStyle[DataFrame]):
    """Extracts data from Excel files."""

    def __init__(
        self,
        path: str,
        sheet_name: Optional[Union[str, int]] = 0,
        name: Optional[str] = None,
        read_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(style_name=name or f"excel:{path}")
        self.path = path
        self.sheet_name = sheet_name
        self.read_kwargs = read_kwargs or {}

    def extract(self, source: Optional[DataFrame] = None) -> DataFrame:
        """Extract data from an Excel file.

        Args:
            source: Not used in Excel extraction, here for interface compatibility.

        Returns:
            DataFrame: The extracted data.
        """
        # We ignore source since ExcelExtractionStyle doesn't transform existing data
        df: DataFrame = pd.read_excel(
            self.path,
            sheet_name=self.sheet_name,
            **cast(Dict[str, Any], self.read_kwargs),
        )
        return df


@register_extraction_style("sql")
class SQLExtractionStyle(ExtractionStyle[DataFrame]):
    """Executes SQL queries against a database connection."""

    def __init__(
        self,
        connection_string: str,
        query: str,
        name: Optional[str] = None,
        read_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(style_name=name or f"sql:{query[:20]}")
        self.connection_string = connection_string
        self.query = query
        self.read_kwargs = read_kwargs or {}

    def extract(self, source: Optional[DataFrame] = None) -> DataFrame:
        """Extract data from a SQL database.

        Args:
            source: Not used in SQL extraction, here for interface compatibility.

        Returns:
            DataFrame: The extracted data.
        """
        try:
            from sqlalchemy import create_engine
        except ImportError as e:
            raise RuntimeError(
                "SQLExtractionStyle requires SQLAlchemy. Install it with `pip install sqlalchemy`."
            ) from e

        engine = create_engine(self.connection_string)
        with engine.connect() as conn:
            df: DataFrame = pd.read_sql_query(
                sql=self.query, con=conn, **cast(Dict[str, Any], self.read_kwargs)
            )
        return df


@register_extraction_style("api")
class APIExtractionStyle(ExtractionStyle[DataFrame]):
    """Fetches data from a REST API endpoint."""

    def __init__(
        self,
        endpoint: str,
        params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        name: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(style_name=name or f"api:{endpoint[:30]}")
        self.endpoint = endpoint
        self.params = params or {}
        self.headers = headers or {}
        self.timeout = timeout

    def extract(self, source: Optional[DataFrame] = None) -> DataFrame:
        """Extract data from a REST API endpoint.

        Args:
            source: Not used in API extraction, here for interface compatibility.

        Returns:
            DataFrame: The extracted data.
        """
        response = requests.get(
            self.endpoint,
            params=self.params,
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        result_data = response.json()

        # Convert JSON data to DataFrame
        if isinstance(result_data, list):
            return pd.DataFrame(result_data)
        elif isinstance(result_data, dict):
            # Try to handle nested structures by normalizing
            return pd.json_normalize(result_data)
        else:
            raise ValueError(f"Unexpected API response type: {type(result_data)}")
