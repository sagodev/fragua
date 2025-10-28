"""
DeliveryStyle types for various data delivery methods.
"""

from abc import abstractmethod
from typing import Any, Generic

from sqlalchemy import create_engine
import pandas as pd
import requests

from fragua.core.base_style import BaseStyle, ResultT
from fragua.params.delivery_params import DeliveryParamsT
from fragua.utils.logger import get_logger
from fragua.params.delivery_params import (
    ExcelDeliveryParamsT,
    SQLDeliveryParamsT,
    APIDeliveryParamsT,
)
from .styles_registry import register_style


logger = get_logger(__name__)

action: str = "deliver"


# ---------------------------------------------------------------------- #
# Base DeliveryStyle
# ---------------------------------------------------------------------- #
class DeliveryStyle(
    BaseStyle[DeliveryParamsT, ResultT], Generic[DeliveryParamsT, ResultT]
):
    """
    Base class for all delivery styles in Fragua ETL.

    Standard pipeline provided by BaseStyle:
        validate_params -> _run -> validate_result -> postprocess
    """

    # ---------------------------------------------------------------------- #
    # Abstract delivery method
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def deliver(self, params: DeliveryParamsT) -> ResultT:
        """
        Deliver the given data to the target destination.
        Must be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement deliver()")

    # ---------------------------------------------------------------------- #
    # Optional parameter validation hook
    # ---------------------------------------------------------------------- #
    def validate_params(self, params: DeliveryParamsT) -> DeliveryParamsT:
        """Validate delivery-specific input parameters."""
        super().validate_params(params)

        if not getattr(params, "destination", None):
            raise ValueError(f"{self.style_name}: 'destination' is required.")

        return params

    # ---------------------------------------------------------------------- #
    # Internal _run implementation for BaseStyle
    # ---------------------------------------------------------------------- #
    def _run(self, params: DeliveryParamsT) -> ResultT:
        """
        Executes the DeliveryStyle delivery step.

        This method is called by BaseStyle.use().
        """
        logger.debug("Starting DeliveryStyle '%s' delivery.", self.style_name)
        result = self.deliver(params)
        logger.debug("DeliveryStyle '%s' delivery completed.", self.style_name)
        return result


# ---------------------------------------------------------------------- #
# Excel Delivery Style
# ---------------------------------------------------------------------- #
@register_style(action, "excel")
class ExcelDeliveryStyle(DeliveryStyle[ExcelDeliveryParamsT, pd.DataFrame]):
    """DeliveryStyle for exporting data to Excel files."""

    def deliver(self, params: ExcelDeliveryParamsT) -> pd.DataFrame:
        """Export data to an Excel file."""
        data = params.data

        if not isinstance(data, pd.DataFrame):
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
@register_style(action, "sql")
class SQLDeliveryStyle(DeliveryStyle[SQLDeliveryParamsT, pd.DataFrame]):
    """DeliveryStyle for delivering data to SQL databases."""

    def deliver(self, params: SQLDeliveryParamsT) -> pd.DataFrame:
        """Deliver data to SQL database."""
        data = params.data
        if not isinstance(data, pd.DataFrame):
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
@register_style(action, "api")
class APIDeliveryStyle(DeliveryStyle[APIDeliveryParamsT, Any]):
    """DeliveryStyle for delivering data to external APIs."""

    def deliver(self, params: APIDeliveryParamsT) -> Any:
        """Deliver data to REST API endpoint."""
        data = params.data
        endpoint = params.endpoint
        if not endpoint:
            raise ValueError("endpoint is required")

        # Prepare headers
        headers: dict[Any, Any] = params.headers or {}
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
