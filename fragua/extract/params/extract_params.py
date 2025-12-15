"""
Extract parameter classes for supported data source types.

Each class defines the configuration schema required to extract data
from a specific source type and is consumed by extract styles during
the extraction workflow.
"""

from typing import Any, Dict, Optional, Type, Union
from pathlib import Path

from fragua.extract.params.base import ExtractParams

# pylint: disable=too-many-arguments, too-many-positional-arguments
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods


class CSVExtractParams(ExtractParams):
    """
    Extraction parameters for CSV file sources.
    """

    purpose = "Parameters required to extract data from a CSV file."

    FIELD_DESCRIPTIONS = {
        "path": "Filesystem path to the CSV file.",
    }

    def __init__(self, path: Optional[Union[str, Path]] = None) -> None:
        """
        Initialize CSV extraction parameters.

        Args:
            path: Path to the CSV file.
        """
        super().__init__(style="csv")
        self.path = None if not path else Path(path)


class ExcelExtractParams(ExtractParams):
    """
    Extraction parameters for Excel file sources.
    """

    purpose = "Parameters required to extract data from an Excel file."

    FIELD_DESCRIPTIONS = {
        "path": "Filesystem path to the Excel file.",
        "sheet_name": "Name or index of the worksheet to load.",
    }

    def __init__(
        self,
        path: Optional[Union[str, Path]] = None,
        sheet_name: Union[str, int] = 0,
    ) -> None:
        """
        Initialize Excel extraction parameters.

        Args:
            path: Path to the Excel file.
            sheet_name: Worksheet name or index.
        """
        super().__init__(style="excel")
        self.path = None if not path else Path(path)
        self.sheet_name = sheet_name


class SQLExtractParams(ExtractParams):
    """
    Extraction parameters for SQL database sources.
    """

    purpose = "Parameters required to extract data from a SQL database."

    FIELD_DESCRIPTIONS = {
        "connection_string": "Database connection URL string.",
        "query": "SQL query to be executed.",
    }

    def __init__(
        self,
        connection_string: Optional[str] = None,
        query: Optional[str] = None,
    ) -> None:
        """
        Initialize SQL extraction parameters.

        Args:
            connection_string: Database connection URL.
            query: SQL query to execute.
        """
        super().__init__(style="sql")
        self.connection_string = connection_string
        self.query = query


class APIExtractParams(ExtractParams):
    """
    Extraction parameters for HTTP API sources.
    """

    purpose = "Parameters required to extract data from an API endpoint."

    FIELD_DESCRIPTIONS = {
        "url": "Full URL of the API endpoint.",
        "method": "HTTP method to use (GET, POST, etc).",
        "headers": "HTTP headers sent with the request.",
        "params": "URL query parameters sent with the request.",
        "data": "Body data sent for POST/PUT requests.",
        "auth": "Authentication credentials (API dependent).",
        "proxy": "Proxy configuration for routing the request.",
        "timeout": "Maximum time in seconds to wait for a response.",
    }

    def __init__(
        self,
        url: Optional[str] = None,
        method: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        auth: Optional[Dict[str, str]] = None,
        proxy: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
    ) -> None:
        """
        Initialize API extraction parameters.

        Args:
            url: API endpoint URL.
            method: HTTP method to use.
            headers: HTTP headers.
            params: URL query parameters.
            data: Request body payload.
            auth: Authentication configuration.
            proxy: Proxy configuration.
            timeout: Request timeout in seconds.
        """
        super().__init__(style="api")
        self.url = "" if url else url
        self.method = "GET" if not method else method
        self.headers = {} if not headers else headers
        self.params = {} if not params else params
        self.data = {} if not data else data
        self.auth = {} if not auth else auth
        self.proxy = {} if not proxy else proxy
        self.timeout = timeout


EXTRACT_PARAMS_CLASSES: Dict[str, Type[ExtractParams]] = {
    "csv": CSVExtractParams,
    "excel": ExcelExtractParams,
    "sql": SQLExtractParams,
    "api": APIExtractParams,
}
