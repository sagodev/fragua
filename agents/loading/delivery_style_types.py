"""
SubTypes of DeliveryStyle representing specific delivery methods with a unified delivery method.
"""

from typing import Any
import requests
from sqlalchemy import create_engine
import pandas as pd
from agents.loading.delivery_style import DeliveryStyle, register_delivery_style


@register_delivery_style("excel")
class ExcelDeliveryStyle(DeliveryStyle):
    """DeliveryStyle for exporting data to Excel files."""

    def __init__(self, style_name: str, destination: str):
        super().__init__(style_name)
        self.destination = destination  # path del archivo Excel

    def deliver(self, data: Any) -> Any:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("ExcelDeliveryStyle requires a pandas DataFrame")
        data.to_excel(self.destination, index=False)
        logger.info(f"{self.style_name} delivered data to {self.destination}")
        return data  # devuelve la data para continuar pipeline


@register_delivery_style("sql")
class SQLDeliveryStyle(DeliveryStyle):
    """DeliveryStyle for delivering data to SQL databases."""

    def __init__(self, style_name: str, connection_string: str, table_name: str):
        super().__init__(style_name)
        self.connection_string = connection_string
        self.table_name = table_name
        self.destination = f"SQL Table: {table_name}"

    def deliver(self, data: Any) -> Any:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("SQLDeliveryStyle requires a pandas DataFrame")
        engine = create_engine(self.connection_string)
        data.to_sql(self.table_name, engine, if_exists="replace", index=False)
        engine.dispose()
        logger.info(f"{self.style_name} delivered data to table '{self.table_name}'")
        return data


@register_delivery_style("api")
class APIDeliveryStyle(DeliveryStyle):
    """DeliveryStyle for delivering data to external APIs."""

    def __init__(self, style_name: str, api_endpoint: str, api_key: str | None = None):
        super().__init__(style_name)
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.destination = f"API: {api_endpoint}"

    def deliver(self, data: Any) -> Any:
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        response = requests.post(self.api_endpoint, json=data, headers=headers)
        response.raise_for_status()
        logger.info(f"{self.style_name} delivered data to API {self.api_endpoint}")
        return data
