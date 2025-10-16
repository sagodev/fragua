"""
Concrete ExtractionStyle classes with dynamic registration for Fragua ETL.
Replaces the old Pickaxe-based system.
"""

from typing import Optional
import pandas as pd
import requests
from agents.extraction.extraction_style import (
    ExtractionStyle,
    register_extraction_style,
)

from agents.store.wagon import Wagon


@register_extraction_style("csv")
class CSVExtractionStyle(ExtractionStyle):
    """Extracts data from CSV files."""

    def __init__(
        self, path: str, name: Optional[str] = None, read_kwargs: Optional[dict] = None
    ):
        super().__init__(style_name=name or f"csv:{path}")
        self.path = path
        self.read_kwargs = read_kwargs or {}

    def extract(self, source=None) -> Wagon:
        df = pd.read_csv(self.path, **self.read_kwargs)
        return Wagon(name=self.style_name, data=df)


@register_extraction_style("excel")
class ExcelExtractionStyle(ExtractionStyle):
    """Extracts data from Excel files."""

    def __init__(
        self,
        path: str,
        sheet_name: Optional[str | int] = 0,
        name: Optional[str] = None,
        read_kwargs: Optional[dict] = None,
    ):
        super().__init__(style_name=name or f"excel:{path}")
        self.path = path
        self.sheet_name = sheet_name
        self.read_kwargs = read_kwargs or {}

    def extract(self, source=None) -> Wagon:
        df = pd.read_excel(self.path, sheet_name=self.sheet_name, **self.read_kwargs)
        return Wagon(name=self.style_name, data=df)


@register_extraction_style("sql")
class SQLExtractionStyle(ExtractionStyle):
    """Executes SQL queries against a database connection."""

    def __init__(
        self,
        connection_string: str,
        query: str,
        name: Optional[str] = None,
        read_kwargs: Optional[dict] = None,
    ):
        super().__init__(style_name=name or f"sql:{query[:20]}")
        self.connection_string = connection_string
        self.query = query
        self.read_kwargs = read_kwargs or {}

    def extract(self, source=None) -> Wagon:
        try:
            from sqlalchemy import create_engine
        except ImportError as e:
            raise RuntimeError(
                "SQLExtractionStyle requires SQLAlchemy. Install it with `pip install sqlalchemy`."
            ) from e

        engine = create_engine(self.connection_string)
        with engine.connect() as conn:
            df = pd.read_sql(self.query, con=conn, **self.read_kwargs)
        return Wagon(name=self.style_name, data=df)


@register_extraction_style("api")
class APIExtractionStyle(ExtractionStyle):
    """Fetches data from a REST API endpoint."""

    def __init__(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        name: Optional[str] = None,
    ):
        super().__init__(style_name=name or f"api:{endpoint[:30]}")
        self.endpoint = endpoint
        self.params = params or {}
        self.headers = headers or {}

    def extract(self, source=None) -> Wagon:
        response = requests.get(self.endpoint, params=self.params, headers=self.headers)
        response.raise_for_status()
        result_data = response.json()
        return Wagon(name=self.style_name, data=result_data)
