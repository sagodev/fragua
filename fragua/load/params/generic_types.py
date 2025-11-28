"""Generic Types for Load Params Classes."""

from typing import TypeVar
from fragua.load.params.base import LoadParams
from fragua.load.params.load_params import APILoadParams, ExcelLoadParams, SQLLoadParams


LoadParamsT = TypeVar("LoadParamsT", bound=LoadParams)
ExcelLoadParamsT = TypeVar("ExcelLoadParamsT", bound=ExcelLoadParams)
SQLLoadParamsT = TypeVar("SQLLoadParamsT", bound=SQLLoadParams)
APILoadParamsT = TypeVar("APILoadParamsT", bound=APILoadParams)
