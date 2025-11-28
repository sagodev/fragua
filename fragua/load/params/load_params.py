"""
Load parameters classes for different types of data destinations.
"""

from typing import Dict
from pandas import DataFrame

from fragua.load.params.base import LoadParams

# pylint: disable=too-many-arguments, too-many-positional-arguments


class ExcelLoadParams(LoadParams):
    """Parameters for Excel load."""

    file_name: str | None
    sheet_name: str | None
    index: bool
    engine: str | None

    purpose = "Parameters required to load data into an Excel file."

    FIELD_DESCRIPTIONS = {
        "data": "Pandas DataFrame containing the data to be written to Excel.",
        "destination": "Optional directory or full path where the file will be saved.",
        "file_name": "Name of the Excel file to create or overwrite.",
        "sheet_name": "Name of the worksheet where data will be written.",
        "index": "Whether to write row indices to the Excel file.",
        "engine": "Optional Excel writer engine (e.g., openpyxl, xlsxwriter).",
    }

    def __init__(
        self,
        data: DataFrame,
        destination: str | None = None,
        file_name: str | None = None,
        sheet_name: str | None = None,
        index: bool = False,
        engine: str | None = None,
    ) -> None:
        super().__init__(style="excel", data=data, destination=destination)
        self.file_name = file_name
        self.sheet_name = sheet_name
        self.index = index
        self.engine = engine


class SQLLoadParams(LoadParams):
    """Parameters for SQL load."""

    table_name: str | None
    if_exists: str
    index: bool
    chunksize: int | None

    purpose = "Parameters required to load data into a SQL database table."

    FIELD_DESCRIPTIONS = {
        "data": "Pandas DataFrame containing the data to be inserted.",
        "destination": "Optional database target (e.g., connection alias).",
        "table_name": "Name of the SQL table where the data will be written.",
        "if_exists": "Behavior when the table already exists: fail, replace, or append.",
        "index": "Whether to write row indices to the SQL table.",
        "chunksize": "Number of rows per batch insert operation.",
    }

    def __init__(
        self,
        data: DataFrame,
        destination: str | None = None,
        table_name: str | None = None,
        if_exists: str = "fail",
        index: bool = False,
        chunksize: int | None = None,
    ) -> None:
        super().__init__(style="sql", data=data, destination=destination)
        self.table_name = table_name
        self.if_exists = if_exists
        self.index = index
        self.chunksize = chunksize


class APILoadParams(LoadParams):
    """Parameters for API load."""

    endpoint: str | None
    method: str
    headers: Dict[str, str]
    auth: Dict[str, str]
    timeout: float

    purpose = "Parameters required to send data to a remote API."

    FIELD_DESCRIPTIONS = {
        "data": "Pandas DataFrame to be serialized and sent via API request.",
        "destination": "Optional identifier for the API service.",
        "endpoint": "URL endpoint where the DataFrame will be submitted.",
        "method": "HTTP method to use (POST, PUT, etc).",
        "headers": "HTTP request headers.",
        "auth": "Authentication parameters (e.g., tokens, API keys).",
        "timeout": "Maximum number of seconds to wait for the API response.",
    }

    def __init__(
        self,
        data: DataFrame,
        destination: str | None = None,
        endpoint: str | None = None,
        method: str = "POST",
        headers: Dict[str, str] | None = None,
        auth: Dict[str, str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(style="api", data=data, destination=destination)
        self.endpoint = endpoint
        self.method = method
        self.headers = headers or {}
        self.auth = auth or {}
        self.timeout = timeout
