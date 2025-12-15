"""
Load parameter classes for different data destinations.

Each LoadParams subclass defines the configuration schema required
by a specific load style and its corresponding load function.
"""

from typing import Dict, Optional, Type
from pandas import DataFrame

from fragua.load.params.base import LoadParams

# pylint: disable=too-many-arguments, too-many-positional-arguments
# pylint: disable=too-few-public-methods


class ExcelLoadParams(LoadParams):
    """
    Parameters for loading data into Excel files.

    Encapsulates all configuration values required to persist
    a pandas DataFrame into an Excel workbook.
    """

    purpose = "Parameters required to load data into an Excel file."

    FIELD_DESCRIPTIONS = {
        "data": "Pandas DataFrame containing the data to be written to Excel.",
        "destination": "Target directory or full path where the Excel file will be saved.",
        "file_name": "Name of the Excel file to create or overwrite.",
        "sheet_name": "Worksheet name where the data will be written.",
        "index": "Whether to include DataFrame row indices in the output file.",
        "engine": "Optional Excel writer engine (e.g., openpyxl, xlsxwriter).",
    }

    def __init__(
        self,
        data: Optional[DataFrame] = None,
        destination: Optional[str] = None,
        file_name: Optional[str] = None,
        sheet_name: Optional[str] = None,
        index: bool = False,
        engine: Optional[str] = None,
    ) -> None:
        """
        Initialize Excel load parameters.

        Args:
            data (Optional[DataFrame]):
                DataFrame to be exported.
            destination (Optional[str]):
                Target directory or full file path.
            file_name (Optional[str]):
                Excel file name.
            sheet_name (Optional[str]):
                Target worksheet name.
            index (bool):
                Whether to write row indices.
            engine (Optional[str]):
                Excel writer engine to use.
        """
        super().__init__(style="excel")
        self.data = data if data is not None else DataFrame()
        self.destination = destination if destination else ""
        self.file_name = file_name if file_name else ""
        self.sheet_name = sheet_name if sheet_name else ""
        self.index = index
        self.engine = engine if engine else ""


class SQLLoadParams(LoadParams):
    """
    Parameters for loading data into SQL database tables.

    Defines the configuration required to insert a DataFrame
    into a relational database using a load style.
    """

    purpose = "Parameters required to load data into a SQL database table."

    FIELD_DESCRIPTIONS = {
        "data": "Pandas DataFrame containing the data to be inserted.",
        "destination": "Database target or connection identifier.",
        "table_name": "Name of the target SQL table.",
        "if_exists": "Behavior when the table already exists (fail, replace, append).",
        "index": "Whether to persist DataFrame indices as table columns.",
        "chunksize": "Number of rows per batch insert operation.",
    }

    def __init__(
        self,
        data: Optional[DataFrame] = None,
        destination: Optional[str] = None,
        table_name: Optional[str] = None,
        if_exists: str = "fail",
        index: bool = False,
        chunksize: Optional[int] = None,
    ) -> None:
        """
        Initialize SQL load parameters.

        Args:
            data (Optional[DataFrame]):
                DataFrame to be inserted.
            destination (Optional[str]):
                Database connection or alias.
            table_name (Optional[str]):
                Target table name.
            if_exists (str):
                Behavior if the table already exists.
            index (bool):
                Whether to include DataFrame indices.
            chunksize (Optional[int]):
                Batch size for insert operations.
        """
        super().__init__(style="sql")
        self.data = data if data is not None else DataFrame()
        self.destination = destination if destination else ""
        self.table_name = table_name if table_name else ""
        self.if_exists = if_exists
        self.index = index
        self.chunksize = chunksize


class APILoadParams(LoadParams):
    """
    Parameters for sending data to remote APIs.

    Defines the configuration required to serialize and submit
    a DataFrame via HTTP requests.
    """

    purpose = "Parameters required to send data to a remote API."

    FIELD_DESCRIPTIONS = {
        "data": "Pandas DataFrame to be serialized and sent in the request body.",
        "destination": "Optional identifier for the API service.",
        "endpoint": "Target API endpoint URL.",
        "method": "HTTP method to use (POST, PUT, etc.).",
        "headers": "HTTP request headers.",
        "auth": "Authentication configuration (tokens, API keys, etc.).",
        "timeout": "Maximum time in seconds to wait for the API response.",
    }

    def __init__(
        self,
        data: Optional[DataFrame] = None,
        destination: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        headers: Optional[Dict[str, str]] | None = None,
        auth: Optional[Dict[str, str]] | None = None,
        timeout: float = 30.0,
    ) -> None:
        """
        Initialize API load parameters.

        Args:
            data (Optional[DataFrame]):
                DataFrame to be serialized and transmitted.
            destination (Optional[str]):
                Logical API service identifier.
            endpoint (Optional[str]):
                Target API URL.
            method (Optional[str]):
                HTTP method to use.
            headers (Optional[Dict[str, str]]):
                HTTP request headers.
            auth (Optional[Dict[str, str]]):
                Authentication configuration.
            timeout (float):
                Request timeout in seconds.
        """
        super().__init__(style="api")
        self.data = data if data is not None else DataFrame()
        self.destination = destination if destination else ""
        self.endpoint = endpoint if endpoint else ""
        self.method = method if method else "POST"
        self.headers = headers if headers else {}
        self.auth = auth if auth else {}
        self.timeout = timeout


LOAD_PARAMS_CLASSES: Dict[str, Type[LoadParams]] = {
    "excel": ExcelLoadParams,
    "sql": SQLLoadParams,
    "api": APILoadParams,
}
