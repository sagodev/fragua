"""
Delivery parameters classes for different types of data destinations.
"""

from typing import Dict, TypeVar
from pandas import DataFrame
from fragua.core.params import BaseParams, register_params

agent: str = "transporter"


class DeliveryParams(BaseParams):
    """Common parameters for delivery agents."""

    data: DataFrame
    destination: str


@register_params(agent, style="excel")
class ExcelDeliveryParams(DeliveryParams):
    """Parameters for Excel delivery."""

    sheet_name: str | None = None
    index: bool = False
    engine: str | None = None


@register_params(agent, style="sql")
class SQLDeliveryParams(DeliveryParams):
    """Parameters for SQL delivery."""

    table_name: str
    if_exists: str = "fail"
    index: bool = False
    chunksize: int | None = None


@register_params(agent, style="api")
class APIDeliveryParams(DeliveryParams):
    """Parameters for API delivery."""

    endpoint: str
    method: str = "POST"
    headers: Dict[str, str] | None = None
    auth: Dict[str, str] | None = None
    timeout: float = 30.0


DeliveryParamsT = TypeVar("DeliveryParamsT", bound=DeliveryParams)
ExcelDeliveryParamsT = TypeVar("ExcelDeliveryParamsT", bound=ExcelDeliveryParams)
SQLDeliveryParamsT = TypeVar("SQLDeliveryParamsT", bound=SQLDeliveryParams)
APIDeliveryParamsT = TypeVar("APIDeliveryParamsT", bound=APIDeliveryParams)
