"""Generic Types for Extract Params Classes."""

from typing import TypeVar

from fragua.extract.params.base import ExtractParams
from fragua.extract.params.extract_params import (
    APIExtractParams,
    CSVExtractParams,
    ExcelExtractParams,
    SQLExtractParams,
)


ExtractParamsT = TypeVar("ExtractParamsT", bound=ExtractParams)
CSVExtractParamsT = TypeVar("CSVExtractParamsT", bound=CSVExtractParams)
ExcelExtractParamsT = TypeVar("ExcelExtractParamsT", bound=ExcelExtractParams)
SQLExtractParamsT = TypeVar("SQLExtractParamsT", bound=SQLExtractParams)
APIExtractParamsT = TypeVar("APIExtractParamsT", bound=APIExtractParams)
