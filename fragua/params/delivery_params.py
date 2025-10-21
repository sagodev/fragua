"""
Delivery parameters classes for different types of data destinations.
"""

from typing import Dict

from pandas import DataFrame
from fragua.core.base_params import BaseParams


class DeliveryParams(BaseParams):
    """Common parameters for delivery agents."""

    data: DataFrame
    destination: str


class ExcelDeliveryParams(DeliveryParams):
    """Parameters for Excel delivery."""

    sheet_name: str | None = None
    index: bool = False
    engine: str | None = None


class SQLDeliveryParams(DeliveryParams):
    """Parameters for SQL delivery."""

    table_name: str
    if_exists: str = "fail"
    index: bool = False
    chunksize: int | None = None


class APIDeliveryParams(DeliveryParams):
    """Parameters for API delivery."""

    endpoint: str
    method: str = "POST"
    headers: Dict[str, str] | None = None
    auth: Dict[str, str] | None = None
    timeout: float = 30.0
