"""
DeliveryStyle types for various data delivery methods.
"""

from abc import abstractmethod
from typing import Any, Generic
import os

from sqlalchemy import create_engine
import pandas as pd
import requests

from fragua.style.style import Style, ResultT, register_style
from fragua.params.delivery_params import DeliveryParamsT
from fragua.utils.logger import get_logger
from fragua.params.delivery_params import (
    ExcelDeliveryParamsT,
    SQLDeliveryParamsT,
    APIDeliveryParamsT,
)


logger = get_logger(__name__)

action: str = "deliver"


# ---------------------------------------------------------------------- #
# Base DeliveryStyle
# ---------------------------------------------------------------------- #
class DeliveryStyle(Style[DeliveryParamsT, ResultT], Generic[DeliveryParamsT, ResultT]):
    """
    Base class for all delivery styles in Fragua ETL.

    Standard pipeline provided by Style:
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
    # Internal _run implementation for Style
    # ---------------------------------------------------------------------- #
    def _run(self, params: DeliveryParamsT) -> ResultT:
        """
        Executes the DeliveryStyle delivery step.

        This method is called by Style.use().
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
        """Export data to an Excel file.
        If the file exists, append the DataFrame as a new sheet instead of overwriting.
        """

        data = params.data
        if not isinstance(data, pd.DataFrame):
            raise TypeError("ExcelDeliveryStyle requires a pandas DataFrame")

        # -----------------------------
        # Build full file path
        # -----------------------------
        destination_dir = params.destination
        file_name = params.file_name or "output.xlsx"
        os.makedirs(destination_dir, exist_ok=True)

        destination = os.path.join(destination_dir, file_name)
        sheet_name = params.sheet_name or "Sheet1"

        # -----------------------------
        # Convert timezone-aware datetime columns to naive
        # -----------------------------
        datetime_cols = data.select_dtypes(include=["datetimetz"]).columns
        if len(datetime_cols) > 0:
            data = data.copy()
            for col in datetime_cols:
                data[col] = data[col].dt.tz_convert(None)
            logger.debug(
                "Converted timezone-aware datetime columns to naive: %s",
                list(datetime_cols),
            )

        # -----------------------------
        # Write or append to Excel file
        # -----------------------------
        if os.path.exists(destination):
            with pd.ExcelWriter(
                destination,
                mode="a",
                engine="openpyxl",
                if_sheet_exists="new",
            ) as writer:
                data.to_excel(writer, sheet_name=sheet_name, index=params.index)
                logger.info(
                    "Appended new sheet '%s' to existing file %s",
                    sheet_name,
                    destination,
                )
        else:
            with pd.ExcelWriter(destination, engine="openpyxl") as writer:
                data.to_excel(writer, sheet_name=sheet_name, index=params.index)
                logger.info(
                    "Created new Excel file %s with sheet '%s'",
                    destination,
                    sheet_name,
                )

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
