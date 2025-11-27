"""
Extract parameters classes for different types of data sources.
"""

from typing import Any, Dict, Union, TypeVar
from pathlib import Path
from fragua.params.params import Params

# pylint: disable=too-many-arguments, too-many-positional-arguments
# pylint: disable=too-many-instance-attributes


class ExtractParams(Params):
    """Common parameters for extraction agents."""

    read_kwargs: Dict[str, Any]

    purpose: str | None = (
        "Base extraction parameters used across all extract-style agents."
    )

    FIELD_DESCRIPTIONS = {
        "read_kwargs": "Additional keyword arguments passed to the data reader.",
    }

    def __init__(self, style: str, read_kwargs: Dict[str, Any] | None = None) -> None:
        super().__init__(action="extract", style=style)
        self.read_kwargs = read_kwargs or {}


class CSVExtractParams(ExtractParams):
    """Extraction parameters for CSV files."""

    path: Path

    purpose = "Parameters required to extract data from a CSV file."

    FIELD_DESCRIPTIONS = {
        "path": "Filesystem path to the CSV file.",
        "read_kwargs": "Additional keyword arguments passed to the CSV reader.",
    }

    def __init__(
        self, path: Union[str, Path], read_kwargs: Dict[str, Any] | None = None
    ) -> None:
        super().__init__(style="csv", read_kwargs=read_kwargs)
        self.path = Path(path)


class ExcelExtractParams(ExtractParams):
    """Extraction parameters for Excel files."""

    path: Path
    sheet_name: Union[str, int]

    purpose = "Parameters required to extract data from an Excel file."

    FIELD_DESCRIPTIONS = {
        "path": "Filesystem path to the Excel file.",
        "sheet_name": "Name or index of the worksheet to load.",
        "read_kwargs": "Additional keyword arguments passed to the Excel reader.",
    }

    def __init__(
        self,
        path: Union[str, Path],
        sheet_name: Union[str, int] = 0,
        read_kwargs: Dict[str, Any] | None = None,
    ) -> None:
        super().__init__(style="excel", read_kwargs=read_kwargs)
        self.path = Path(path)
        self.sheet_name = sheet_name


class SQLExtractParams(ExtractParams):
    """Extraction parameters for SQL databases."""

    connection_string: str
    query: str

    purpose = "Parameters required to extract data from a SQL database."

    FIELD_DESCRIPTIONS = {
        "connection_string": "Database connection URL string.",
        "query": "SQL query to be executed.",
    }

    def __init__(self, connection_string: str, query: str) -> None:
        super().__init__(style="sql")
        self.connection_string = connection_string
        self.query = query


class APIExtractParams(ExtractParams):
    """Extraction parameters for APIs."""

    url: str
    method: str
    headers: Dict[str, str]
    params: Dict[str, Any]
    data: Dict[str, Any]
    auth: Dict[str, str]
    proxy: Dict[str, str]
    timeout: float

    purpose = "Parameters required to extract data from an API endpoint."

    FIELD_DESCRIPTIONS = {
        "url": "Full URL of the API endpoint.",
        "method": "HTTP method to use (GET, POST, etc).",
        "headers": "HTTP headers sent with the request.",
        "params": "URL query parameters sent with the request.",
        "data": "Body data sent for POST/PUT requests.",
        "auth": "Authentication credentials (varies by API).",
        "proxy": "Proxy configuration for routing the request.",
        "timeout": "Maximum time in seconds to wait for a response.",
    }

    def __init__(
        self,
        url: str,
        method: str = "GET",
        headers: Dict[str, str] | None = None,
        params: Dict[str, Any] | None = None,
        data: Dict[str, Any] | None = None,
        auth: Dict[str, str] | None = None,
        proxy: Dict[str, str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(style="api")
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.params = params or {}
        self.data = data or {}
        self.auth = auth or {}
        self.proxy = proxy or {}
        self.timeout = timeout


ExtractParamsT = TypeVar("ExtractParamsT", bound=ExtractParams)
CSVExtractParamsT = TypeVar("CSVExtractParamsT", bound=CSVExtractParams)
ExcelExtractParamsT = TypeVar("ExcelExtractParamsT", bound=ExcelExtractParams)
SQLExtractParamsT = TypeVar("SQLExtractParamsT", bound=SQLExtractParams)
APIExtractParamsT = TypeVar("APIExtractParamsT", bound=APIExtractParams)


EXTRACT_PARAMS_CLASSES: Dict[str, type[ExtractParams]] = {
    "csv": CSVExtractParams,
    "excel": ExcelExtractParams,
    "sql": SQLExtractParams,
    "api": APIExtractParams,
}
