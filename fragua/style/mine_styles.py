"""
MineStyle types for various data extraction methods.
"""

from abc import abstractmethod
from typing import Any, Generic

from pathlib import Path
from sqlalchemy import create_engine
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth

from fragua.style.style import Style, ResultT, register_style
from fragua.params.mine_params import MineParamsT
from fragua.utils.logger import get_logger
from fragua.params.mine_params import (
    CSVMineParamsT,
    ExcelMineParamsT,
    SQLMineParamsT,
    APIMineParamsT,
)

logger = get_logger(__name__)

action: str = "mine"


# ---------------------------------------------------------------------- #
# Base MineStyle
# ---------------------------------------------------------------------- #
class MineStyle(Style[MineParamsT, ResultT], Generic[MineParamsT, ResultT]):
    """
    Base class for all extraction styles in Fragua ETL.

    Standard pipeline provided by Style:
        validate_params -> _run -> validate_result -> postprocess
    """

    # ---------------------------------------------------------------------- #
    # Abstract extraction method (subclasses implement this)
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def mine(self, params: MineParamsT) -> ResultT:
        """
        Extract data according to source parameters.
        Must be implemented by subclasses.
        """
        raise NotImplementedError

    # ---------------------------------------------------------------------- #
    # Internal _run implementation for Style
    # ---------------------------------------------------------------------- #
    def _run(self, params: MineParamsT) -> ResultT:
        """
        Executes the MineStyle extraction step.

        This method is called by Style.use().
        """
        logger.debug("Starting MineStyle '%s' extraction.", self.style_name)
        result = self.mine(params)
        logger.debug("MineStyle '%s' extraction completed.", self.style_name)
        return result


# ---------------------------------------------------------------------- #
# CSV Extraction
# ---------------------------------------------------------------------- #
@register_style(action, "mine_csv")
class CSVMineStyle(MineStyle[CSVMineParamsT, pd.DataFrame]):
    """Extracts data from CSV files."""

    def mine(self, params: CSVMineParamsT) -> pd.DataFrame:
        path = params.path
        if not path:
            raise ValueError(f"{self.style_name}: 'path' is required in params")

        read_kwargs: dict[Any, Any] = params.read_kwargs or {}

        path_str = str(path) if isinstance(path, Path) else path
        return pd.read_csv(path_str, **read_kwargs)


# ---------------------------------------------------------------------- #
# Excel Extraction
# ---------------------------------------------------------------------- #
@register_style(action, "mine_excel")
class ExcelMineStyle(MineStyle[ExcelMineParamsT, pd.DataFrame]):
    """Extracts data from Excel files."""

    def mine(self, params: ExcelMineParamsT) -> pd.DataFrame:
        path = params.path
        if not path:
            raise ValueError(f"{self.style_name}: 'path' is required in params")

        sheet_name = params.sheet_name
        read_kwargs: dict[Any, Any] = params.read_kwargs or {}

        path_str = str(path) if isinstance(path, Path) else path
        return pd.read_excel(path_str, sheet_name=sheet_name, **read_kwargs)


# ---------------------------------------------------------------------- #
# SQL Extraction
# ---------------------------------------------------------------------- #
@register_style(action, "mine_sql")
class SQLMineStyle(MineStyle[SQLMineParamsT, pd.DataFrame]):
    """Extracts data from SQL databases."""

    def mine(self, params: SQLMineParamsT) -> pd.DataFrame:
        connection_string = params.connection_string
        query = params.query
        if not connection_string or not query:
            raise ValueError(
                f"{self.style_name}: 'connection_string' and 'query' are required in params"
            )

        read_kwargs: dict[Any, Any] = params.read_kwargs or {}

        engine = create_engine(connection_string)
        try:
            with engine.connect() as conn:
                return pd.read_sql_query(query, conn, **read_kwargs)
        finally:
            engine.dispose()


# ---------------------------------------------------------------------- #
# API Extraction
# ---------------------------------------------------------------------- #
@register_style(action, "mine_api")
class APIMineStyle(MineStyle[APIMineParamsT, pd.DataFrame]):
    """Extracts data from REST APIs."""

    def mine(self, params: APIMineParamsT) -> pd.DataFrame:
        url = params.url
        if not url:
            raise ValueError(f"{self.style_name}: 'url' is required in params")

        response = requests.request(
            method=params.method.upper(),
            url=url,
            headers=params.headers,
            params=params.params,
            data=params.data,
            auth=HTTPBasicAuth(**params.auth) if params.auth else None,
            proxies=params.proxy,
            timeout=params.timeout,
        )
        response.raise_for_status()
        result_data = response.json()

        read_kwargs: dict[Any, Any] = params.read_kwargs or {}
        if isinstance(result_data, list):
            return pd.DataFrame(result_data, **read_kwargs)
        if isinstance(result_data, dict):
            return pd.json_normalize(result_data, **read_kwargs)

        raise ValueError(
            f"{self.style_name}: Unexpected API response type: {type(result_data)}"
        )
