"""
DeliveryStyle types for various data delivery methods.
"""

from typing import Any
import requests
from sqlalchemy import create_engine
from pandas import DataFrame

from fragua.styles.delivery_style import DeliveryStyle, register_delivery_style
from fragua.params.delivery_params import (
    ExcelDeliveryParams,
    SQLDeliveryParams,
    APIDeliveryParams,
)
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


@register_delivery_style("excel")
class ExcelDeliveryStyle(DeliveryStyle[ExcelDeliveryParams, DataFrame]):
    """DeliveryStyle for exporting data to Excel files."""

    def deliver(self, source_params: ExcelDeliveryParams) -> DataFrame:
        """Export data to Excel file.

        Args:
            source_params (ExcelDeliveryParams): Parameters including:
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
        data = source_params.data
        if not isinstance(data, DataFrame):
            raise TypeError("ExcelDeliveryStyle requires a pandas DataFrame")

        destination = source_params.destination
        if not destination:
            raise ValueError("destination is required")

        # Export to Excel
        data.to_excel(
            destination,
            sheet_name=source_params.sheet_name or "Sheet1",
            index=source_params.index,
            engine=source_params.engine,
        )

        logger.info("%s delivered data to %s", self.style_name, destination)
        return data


@register_delivery_style("sql")
class SQLDeliveryStyle(DeliveryStyle[SQLDeliveryParams, DataFrame]):
    """DeliveryStyle for delivering data to SQL databases."""

    def deliver(self, source_params: SQLDeliveryParams) -> DataFrame:
        """Deliver data to SQL database.

        Args:
            source_params (SQLDeliveryParams): Parameters including:
                data (DataFrame): Data to deliver
                destination (str): Database connection string (alias of connection_string)
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
        data = source_params.data
        if not isinstance(data, DataFrame):
            raise TypeError("SQLDeliveryStyle requires a pandas DataFrame")

        connection_string = source_params.destination
        if not connection_string:
            raise ValueError("destination (connection_string) is required")

        table_name = source_params.table_name
        if not table_name:
            raise ValueError("table_name is required")

        # Export to database
        engine = create_engine(connection_string)
        try:
            data.to_sql(
                name=table_name,
                con=engine,
                if_exists=source_params.if_exists,
                index=source_params.index,
                chunksize=source_params.chunksize,
            )
            logger.info("%s delivered data to table '%s'", self.style_name, table_name)
            return data
        finally:
            engine.dispose()


@register_delivery_style("api")
class APIDeliveryStyle(DeliveryStyle[APIDeliveryParams, Any]):
    """DeliveryStyle for delivering data to external APIs."""

    def deliver(self, source_params: APIDeliveryParams) -> Any:
        """Deliver data to REST API endpoint.

        Args:
            source_params (APIDeliveryParams): Parameters including:
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
        data = source_params.data
        endpoint = source_params.endpoint
        if not endpoint:
            raise ValueError("endpoint is required")

        # Prepare headers
        headers = source_params.headers or {}
        if source_params.auth:
            token = source_params.auth.get("token")
            if token:
                headers["Authorization"] = f"Bearer {token}"

        # Make request
        response = requests.request(
            method=source_params.method,
            url=endpoint,
            json=data,
            headers=headers,
            timeout=source_params.timeout,
        )
        response.raise_for_status()

        logger.info("%s delivered data to API %s", self.style_name, endpoint)
        return data
