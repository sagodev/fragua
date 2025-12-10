"""
Load parameters classes for different types of data destinations.
"""

from typing import Dict, Optional, Type
from pandas import DataFrame

from fragua.load.params.base import LoadParams

# pylint: disable=too-many-arguments, too-many-positional-arguments


class ExcelLoadParams(LoadParams):
    """Parameters for Excel load."""

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
        data: Optional[DataFrame] = None,
        destination: Optional[str] = None,
        file_name: Optional[str] = None,
        sheet_name: Optional[str] = None,
        index: bool = False,
        engine: Optional[str] = None,
    ) -> None:
        super().__init__(style="excel")
        self.data = data if data is not None else DataFrame()
        self.destination = destination if destination else ""
        self.file_name = file_name if file_name else ""
        self.sheet_name = sheet_name if sheet_name else ""
        self.index = index
        self.engine = engine if engine else ""


class SQLLoadParams(LoadParams):
    """Parameters for SQL load."""

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
        data: Optional[DataFrame] = None,
        destination: Optional[str] = None,
        table_name: Optional[str] = None,
        if_exists: str = "fail",
        index: bool = False,
        chunksize: Optional[int] = None,
    ) -> None:
        super().__init__(style="sql")
        self.data = data if data is not None else DataFrame()
        self.destination = destination if destination else ""
        self.table_name = table_name if table_name else ""
        self.if_exists = if_exists
        self.index = index
        self.chunksize = chunksize


class APILoadParams(LoadParams):
    """Parameters for API load."""

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
        data: Optional[DataFrame] = None,
        destination: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        headers: Optional[Dict[str, str]] | None = None,
        auth: Optional[Dict[str, str]] | None = None,
        timeout: float = 30.0,
    ) -> None:
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
