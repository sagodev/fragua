"""
Concrete extraction function implementations.

This module provides ExtractFunction implementations for common
data sources such as CSV files, Excel spreadsheets, SQL databases,
and REST APIs.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Type
import pandas as pd
from sqlalchemy import create_engine
import requests
from requests.auth import HTTPBasicAuth


from fragua.extract.functions import ExtractFunction
from fragua.extract.params.extract_params import (
    APIExtractParams,
    CSVExtractParams,
    ExcelExtractParams,
    SQLExtractParams,
)


class CSVExtractFunction(ExtractFunction):
    """
    Extraction function for CSV files.

    Reads a CSV file from disk and returns its contents as a pandas
    DataFrame.
    """

    def __init__(self, params: Optional[CSVExtractParams] = None) -> None:
        """
        Initialize the CSV extract function.

        Args:
            params: Optional CSVExtractParams instance. If not provided,
                a default instance is created.
        """
        super().__init__()
        self.params = CSVExtractParams() if params is None else params

    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of the CSV extract function.

        Returns:
            Dictionary describing the function purpose and parameter type.
        """
        return {
            "function": self.name,
            "params_type": "CSVExtractParams",
            "purpose": "Extract tabular data from a CSV file",
        }

    def execute(self) -> pd.DataFrame:
        """
        Execute the CSV extraction.

        Reads the CSV file defined in the params and loads it into
        a pandas DataFrame.

        Returns:
            A pandas DataFrame containing the extracted data.

        Raises:
            ValueError: If the 'path' parameter is not provided.
        """
        path = self.params.path
        if not path:
            raise ValueError("'path' is required in params")

        path_str = str(path) if isinstance(path, Path) else path
        return pd.read_csv(path_str)


class ExcelExtractFunction(ExtractFunction):
    """
    Extraction function for Excel files.

    Loads data from an Excel spreadsheet into a pandas DataFrame.
    """

    def __init__(self, params: Optional[ExcelExtractParams] = None) -> None:
        """
        Initialize the Excel extract function.

        Args:
            params: Optional ExcelExtractParams instance. If not provided,
                a default instance is created.
        """
        super().__init__()
        self.params = ExcelExtractParams() if params is None else params

    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of the Excel extract function.
        """
        return {
            "function": self.name,
            "params_type": "ExcelExtractParams",
            "purpose": "Extract data from an Excel spreadsheet",
        }

    def execute(self) -> pd.DataFrame:
        """
        Execute the Excel extraction.

        Returns:
            A pandas DataFrame containing the extracted spreadsheet data.

        Raises:
            ValueError: If the 'path' parameter is not provided.
        """
        path = self.params.path
        if not path:
            raise ValueError("'path' is required in params")

        path_str = str(path) if isinstance(path, Path) else path
        return pd.read_excel(path_str, sheet_name=self.params.sheet_name)


class SQLExtractFunction(ExtractFunction):
    """
    Extraction function for SQL databases.

    Executes a SQL query against a database and returns the result
    as a pandas DataFrame.
    """

    def __init__(self, params: Optional[SQLExtractParams] = None) -> None:
        """
        Initialize the SQL extract function.

        Args:
            params: Optional SQLExtractParams instance. If not provided,
                a default instance is created.
        """
        super().__init__()
        self.params = SQLExtractParams() if params is None else params

    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of the SQL extract function.
        """
        return {
            "function": self.name,
            "params_type": "SQLExtractParams",
            "purpose": "Run a SQL query and extract the result as a DataFrame",
        }

    def execute(self) -> pd.DataFrame:
        """
        Execute the SQL extraction.

        Returns:
            A pandas DataFrame containing the query results.

        Raises:
            ValueError: If 'connection_string' or 'query' parameters
                are not provided.
        """
        connection_string = self.params.connection_string
        query = self.params.query
        if not connection_string or not query:
            raise ValueError("'connection_string' and 'query' are required in params")

        engine = create_engine(connection_string)
        try:
            with engine.connect() as conn:
                return pd.read_sql_query(query, conn)
        finally:
            engine.dispose()


class APIExtractFunction(ExtractFunction):
    """
    Extraction function for REST APIs.

    Performs an HTTP request and converts the JSON response into
    a pandas DataFrame.
    """

    def __init__(self, params: Optional[APIExtractParams] = None) -> None:
        """
        Initialize the API extract function.

        Args:
            params: Optional APIExtractParams instance. If not provided,
                a default instance is created.
        """
        super().__init__()
        self.params = APIExtractParams() if params is None else params

    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of the API extract function.
        """
        return {
            "function": self.name,
            "params_type": "APIExtractParams",
            "purpose": "Fetch JSON data from a REST API",
        }

    def execute(self) -> pd.DataFrame:
        """
        Execute the API extraction.

        Sends an HTTP request based on the configured parameters
        and normalizes the JSON response into a DataFrame.

        Returns:
            A pandas DataFrame containing the API response data.

        Raises:
            ValueError: If the 'url' parameter is not provided.
            ValueError: If the API response format is unsupported.
            requests.HTTPError: If the HTTP request fails.
        """
        url = self.params.url
        assert url is not None, "'url' is required in params"

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

        if isinstance(result_data, list):
            return pd.DataFrame(result_data)

        if isinstance(result_data, dict):
            return pd.json_normalize(result_data)

        raise ValueError(f"Unexpected API response type: {type(result_data)}")


EXTRACT_FUNCTION_CLASSES: Dict[str, Type[ExtractFunction]] = {
    "csv": CSVExtractFunction,
    "excel": ExcelExtractFunction,
    "sql": SQLExtractFunction,
    "api": APIExtractFunction,
}
