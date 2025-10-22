"""
DeliveryStyle types for various data delivery methods.
"""

from typing import Any
import requests
from sqlalchemy import create_engine
from pandas import DataFrame

from fragua.styles.delivery_style import DeliveryStyle, register_delivery_style
from fragua.params.delivery_params import (
    ExcelDeliveryParamsT,
    SQLDeliveryParamsT,
    APIDeliveryParamsT,
)
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------- #
# Excel Delivery Style
# ---------------------------------------------------------------------- #
@register_delivery_style("excel")
class ExcelDeliveryStyle(DeliveryStyle[ExcelDeliveryParamsT, DataFrame]):
    """DeliveryStyle for exporting data to Excel files."""

    def deliver(self, params: ExcelDeliveryParamsT) -> DataFrame:
        """Export data to an Excel file."""
        data = params.data

        if not isinstance(data, DataFrame):
            raise TypeError("ExcelDeliveryStyle requires a pandas DataFrame")

        destination = params.destination

        # Convert timezone-aware datetime columns to naive
        datetime_cols = data.select_dtypes(include=["datetimetz"]).columns
        if len(datetime_cols) > 0:
            data = data.copy()
            for col in datetime_cols:
                data[col] = data[col].dt.tz_convert(None)
            logger.debug(
                "Converted timezone-aware datetime columns to naive: %s",
                list(datetime_cols),
            )

        # Export to Excel
        data.to_excel(
            destination,
            sheet_name=params.sheet_name or "Sheet1",
            index=params.index,
            engine=params.engine,
        )

        logger.info("%s delivered data to %s", self.style_name, destination)
        return data


# ---------------------------------------------------------------------- #
# SQL Delivery Style
# ---------------------------------------------------------------------- #
@register_delivery_style("sql")
class SQLDeliveryStyle(DeliveryStyle[SQLDeliveryParamsT, DataFrame]):
    """DeliveryStyle for delivering data to SQL databases."""

    def deliver(self, params: SQLDeliveryParamsT) -> DataFrame:
        """Deliver data to SQL database."""
        data = params.data
        if not isinstance(data, DataFrame):
            raise TypeError("SQLDeliveryStyle requires a pandas DataFrame")

        connection_string = params.destination
        if not connection_string:
            raise ValueError("destination (connection_string) is required")

        table_name = params.table_name
        if not table_name:
            raise ValueError("table_name is required")

        # Export to database
        engine = create_engine(connection_string)
        try:
            data.to_sql(
                name=table_name,
                con=engine,
                if_exists=params.if_exists,
                index=params.index,
                chunksize=params.chunksize,
            )
            logger.info("%s delivered data to table '%s'", self.style_name, table_name)
            return data
        finally:
            engine.dispose()


# ---------------------------------------------------------------------- #
# API Delivery Style
# ---------------------------------------------------------------------- #
@register_delivery_style("api")
class APIDeliveryStyle(DeliveryStyle[APIDeliveryParamsT, Any]):
    """DeliveryStyle for delivering data to external APIs."""

    def deliver(self, params: APIDeliveryParamsT) -> Any:
        """Deliver data to REST API endpoint."""
        data = params.data
        endpoint = params.endpoint
        if not endpoint:
            raise ValueError("endpoint is required")

        # Prepare headers
        headers = params.headers or {}
        if params.auth:
            token = params.auth.get("token")
            if token:
                headers["Authorization"] = f"Bearer {token}"

        # Make request
        response = requests.request(
            method=params.method,
            url=endpoint,
            json=data,
            headers=headers,
            timeout=params.timeout,
        )
        response.raise_for_status()

        logger.info("%s delivered data to API %s", self.style_name, endpoint)
        return data
