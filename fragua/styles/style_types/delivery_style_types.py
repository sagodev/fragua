"""
SubTypes of DeliveryStyle representing specific delivery methods with a unified delivery method.
"""

from typing import Any, Dict, Literal, TypedDict
from typing_extensions import NotRequired
import requests
from sqlalchemy import create_engine
from pandas import DataFrame

from fragua.styles.delivery_style import DeliveryStyle, register_delivery_style
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class ExcelDeliveryParams(TypedDict, total=False):
    """Excel delivery configuration parameters."""

    data: DataFrame
    destination: str
    sheet_name: NotRequired[str]
    index: NotRequired[bool]
    engine: NotRequired[Literal["openpyxl", "xlsxwriter"]]


class SQLDeliveryParams(TypedDict, total=False):
    """SQL delivery configuration parameters."""

    data: DataFrame
    connection_string: str
    table_name: str
    if_exists: NotRequired[Literal["fail", "replace", "append"]]
    index: NotRequired[bool]
    chunksize: NotRequired[int]


class APIDeliveryParams(TypedDict, total=False):
    """API delivery configuration parameters."""

    data: Any
    endpoint: str
    method: NotRequired[Literal["GET", "POST", "PUT", "DELETE", "PATCH"]]
    headers: NotRequired[Dict[str, str]]
    auth: NotRequired[Dict[str, str]]
    timeout: NotRequired[float]


@register_delivery_style("excel")
class ExcelDeliveryStyle(DeliveryStyle[Any, Any]):
    """DeliveryStyle for exporting data to Excel files."""

    def __init__(self, style_name: str) -> None:
        super().__init__(style_name=style_name)

    def deliver(self, source_params: Dict[str, Any]) -> DataFrame:
        """Export data to Excel file.

        Args:
            source_params: Dictionary containing:
                data (DataFrame): Data to export
                destination (str): Excel file path
                sheet_name (str, optional): Sheet name
                index (bool, optional): Whether to write index
                engine (str, optional): Excel writer engine

        Returns:
            DataFrame: The delivered data (unchanged)

        Raises:
            ValueError: If destination is missing
            TypeError: If data is not a DataFrame
        """
        data = source_params["data"]
        if not isinstance(data, DataFrame):
            raise TypeError("ExcelDeliveryStyle requires a pandas DataFrame")

        destination = source_params["destination"]
        if not destination:
            raise ValueError("destination is required")

        # Get optional parameters
        sheet_name = source_params.get("sheet_name", "Sheet1")
        index = source_params.get("index", False)
        engine = source_params.get("engine", None)

        # Export to Excel
        data.to_excel(destination, sheet_name=sheet_name, index=index, engine=engine)
        logger.info("%s delivered data to %s", self.style_name, destination)
        return data


@register_delivery_style("sql")
class SQLDeliveryStyle(DeliveryStyle[Any, Any]):
    """DeliveryStyle for delivering data to SQL databases."""

    def __init__(self, style_name: str) -> None:
        super().__init__(style_name=style_name)

    def deliver(self, source_params: Dict[str, Any]) -> DataFrame:
        """Deliver data to SQL database.

        Args:
            source_params: Dictionary containing:
                data (DataFrame): Data to deliver
                connection_string (str): SQLAlchemy connection URL
                table_name (str): Target table name
                if_exists (str, optional): How to behave if table exists
                index (bool, optional): Whether to write index
                chunksize (int, optional): Rows per chunk

        Returns:
            DataFrame: The delivered data (unchanged)

        Raises:
            ValueError: If connection_string or table_name is missing
            TypeError: If data is not a DataFrame
        """
        data = source_params["data"]
        if not isinstance(data, DataFrame):
            raise TypeError("SQLDeliveryStyle requires a pandas DataFrame")

        connection_string = source_params["connection_string"]
        if not connection_string:
            raise ValueError("connection_string is required")

        table_name = source_params["table_name"]
        if not table_name:
            raise ValueError("table_name is required")

        # Get optional parameters
        if_exists = source_params.get("if_exists", "replace")
        index = source_params.get("index", False)
        chunksize = source_params.get("chunksize", None)

        # Export to database
        engine = create_engine(connection_string)
        try:
            data.to_sql(
                table_name,
                engine,
                if_exists=if_exists,
                index=index,
                chunksize=chunksize,
            )
            logger.info("%s delivered data to table '%s'", self.style_name, table_name)
            return data
        finally:
            engine.dispose()


@register_delivery_style("api")
class APIDeliveryStyle(DeliveryStyle[Any, Any]):
    """DeliveryStyle for delivering data to external APIs."""

    def __init__(self, style_name: str) -> None:
        super().__init__(style_name=style_name)

    def deliver(self, source_params: Dict[str, Any]) -> Any:
        """Deliver data to REST API endpoint.

        Args:
            source_params: Dictionary containing:
                data (Any): Data to deliver
                endpoint (str): API endpoint URL
                method (str, optional): HTTP method
                headers (dict, optional): Request headers
                auth (dict, optional): Basic auth credentials
                timeout (float, optional): Request timeout

        Returns:
            Any: The delivered data (unchanged)

        Raises:
            ValueError: If endpoint is missing
            RequestException: If API request fails
        """
        data = source_params["data"]
        endpoint = source_params["endpoint"]
        if not endpoint:
            raise ValueError("endpoint is required")

        # Get optional parameters
        method = source_params.get("method", "POST")
        headers = source_params.get("headers", {})
        auth = source_params.get("auth", None)
        timeout = source_params.get("timeout", 30.0)

        # Add auth if provided
        if auth:
            headers["Authorization"] = f"Bearer {auth}"

        # Make request
        response = requests.request(
            method=method, url=endpoint, json=data, headers=headers, timeout=timeout
        )
        response.raise_for_status()

        logger.info("%s delivered data to API %s", self.style_name, endpoint)
        return data
