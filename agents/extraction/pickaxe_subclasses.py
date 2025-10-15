"""
Concrete Pickaxe tools for different types of extraction.
"""

from typing import Optional
import pandas as pd
import requests
from agents.extraction.pickaxe import Pickaxe, register_pickaxe
from agents.extraction.wagons import Wagon


@register_pickaxe("csv")
class CSVPickaxe(Pickaxe):
    """
    CSVPickaxe extracts data from CSV files.

    Args:
        path: Filesystem path to CSV.
        name: Optional name for the Pickaxe/Wagon.
        read_kwargs: Optional kwargs forwarded to pandas.read_csv.
    """

    def __init__(
        self, path: str, name: Optional[str] = None, read_kwargs: Optional[dict] = None
    ):
        super().__init__(tool_name=name or f"csv:{path}")
        self.path = path
        self.read_kwargs = read_kwargs or {}

    def extract(self, source=None) -> Wagon:
        """Extracts data from CSV file and wraps it in a Wagon."""
        df = pd.read_csv(self.path, **self.read_kwargs)
        return Wagon(name=self.tool_name, data=df)


@register_pickaxe("excel")
class ExcelPickaxe(Pickaxe):
    """
    ExcelPickaxe extracts data from Excel files.

    Args:
        path: Filesystem path to Excel file.
        sheet_name: Sheet to read (default 0).
        name: Optional name for the Pickaxe/Wagon.
        read_kwargs: Forwarded kwargs to pandas.read_excel.
    """

    def __init__(
        self,
        path: str,
        sheet_name: Optional[str | int] = 0,
        name: Optional[str] = None,
        read_kwargs: Optional[dict] = None,
    ):
        super().__init__(tool_name=name or f"excel:{path}")
        self.path = path
        self.sheet_name = sheet_name
        self.read_kwargs = read_kwargs or {}

    def extract(self, source=None) -> Wagon:
        """Extracts data from Excel file and wraps it in a Wagon."""
        df = pd.read_excel(self.path, sheet_name=self.sheet_name, **self.read_kwargs)
        return Wagon(name=self.tool_name, data=df)


@register_pickaxe("sql")
class SQLPickaxe(Pickaxe):
    """
    SQLPickaxe executes a SQL query against a database connection string.

    Args:
        connection_string: SQLAlchemy connection string (e.g. 'sqlite:///db.sqlite').
        query: SQL query to run.
        name: Optional logical name for the pickaxe.
        read_kwargs: Optional kwargs for pandas.read_sql.
    """

    def __init__(
        self,
        connection_string: str,
        query: str,
        name: Optional[str] = None,
        read_kwargs: Optional[dict] = None,
    ):
        super().__init__(tool_name=name or f"sql:{query[:20]}")
        self.connection_string = connection_string
        self.query = query
        self.read_kwargs = read_kwargs or {}

    def extract(self, source=None) -> Wagon:
        """Executes SQL query and returns a Wagon with the results."""
        try:
            from sqlalchemy import create_engine
        except ImportError as e:
            raise RuntimeError(
                "SQLPickaxe requires SQLAlchemy. Install it with `pip install sqlalchemy`."
            ) from e

        engine = create_engine(self.connection_string)
        with engine.connect() as conn:
            df = pd.read_sql(self.query, con=conn, **self.read_kwargs)
        return Wagon(name=self.tool_name, data=df)


@register_pickaxe("api")
class APIPickaxe(Pickaxe):
    """
    APIPickaxe fetches data from a REST API endpoint.

    Args:
        endpoint: The API endpoint URL.
        params: Query parameters for the request.
        headers: HTTP headers for the request.
        name: Optional logical name for the pickaxe.
    """

    def __init__(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
        name: Optional[str] = None,
    ):
        super().__init__(tool_name=name or f"api:{endpoint[:30]}")
        self.endpoint = endpoint
        self.params = params or {}
        self.headers = headers or {}

    def extract(self, source=None) -> Wagon:
        """Fetches data from the API and wraps it in a Wagon with proper checksum."""
        response = requests.get(self.endpoint, params=self.params, headers=self.headers)
        response.raise_for_status()
        result_data = response.json()

        # If the response is a list of dicts, Wagon.store() will convert it to DataFrame
        # If it's a dict or other structure, Wagon.store() will handle checksum correctly
        return Wagon(name=self.tool_name, data=result_data)
