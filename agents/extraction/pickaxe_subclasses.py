"""
Concrete Pickaxe tools for different types of extraction.
"""

from typing import Optional
import pandas as pd
import requests
from agents.extraction.pickaxe import Pickaxe
from agents.extraction.wagons import Wagon


class CSVPickaxe(Pickaxe):
    """
    CSVPickaxe extracts data from CSV files.

    Args:
        path: filesystem path to CSV.
        name: optional name for the Pickaxe/Wagon.
        read_kwargs: optional kwargs forwarded to pandas.read_csv.
    """

    def __init__(
        self, path: str, name: Optional[str] = None, read_kwargs: Optional[dict] = None
    ):
        super().__init__(tool_name=name or f"csv:{path}")
        self.path = path
        self.read_kwargs = read_kwargs or {}

    def use(self, data=None) -> Wagon:
        """
        Extract data from CSV and store in a Wagon.

        Args:
            data: Not used, present for interface consistency.

        Returns:
            Wagon: Wagon containing extracted data.
        """
        df = pd.read_csv(self.path, **self.read_kwargs)
        wagon = Wagon(name=self.tool_name, data=df)
        return wagon


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

    def use(self, data=None) -> Wagon:
        """
        Extract data from the Excel file and store in a Wagon.

        Args:
            data: Not used (placeholder for compatibility with BaseAgent).

        Returns:
            Wagon: A Wagon containing the extracted data.
        """
        df = pd.read_excel(self.path, sheet_name=self.sheet_name, **self.read_kwargs)
        wagon = Wagon(name=self.tool_name, data=df)
        return wagon


class SQLPickaxe(Pickaxe):
    """
    SQLPickaxe executes a SQL query against a database connection string.

    Args:
        connection_string (str): SQLAlchemy connection string (e.g. 'sqlite:///db.sqlite').
        query (str): SQL query to run.
        name (Optional[str]): Optional logical name for the pickaxe.
        read_kwargs (Optional[dict]): Optional kwargs for pandas.read_sql.
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

    def use(self, data=None) -> Wagon:
        """
        Execute the SQL query and return the results as a Wagon.

        Args:
            data: Not used here.

        Returns:
            Wagon: Contains the query results.
        """
        try:
            # Lazy import to avoid strict dependency if not needed
            from sqlalchemy import create_engine
        except ImportError as e:
            raise RuntimeError(
                "SQLPickaxe requires SQLAlchemy. Install with `pip install sqlalchemy`."
            ) from e

        engine = create_engine(self.connection_string)
        with engine.connect() as conn:
            df = pd.read_sql(self.query, con=conn, **self.read_kwargs)

        wagon = Wagon(name=self.tool_name, data=df)
        return wagon


class APIPickaxe(Pickaxe):
    """
    APIPickaxe fetches data from a REST API endpoint.

    Args:
        endpoint (str): The API endpoint URL.
        params (Optional[dict]): Query parameters for the request.
        headers (Optional[dict]): HTTP headers for the request.
        name (Optional[str]): Optional logical name for the pickaxe.
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

    def use(self, data=None) -> Wagon:
        """
        Execute the API request and return the results as a Wagon.

        Args:
            data: Not used here.

        Returns:
            Wagon: Contains the API response data (usually JSON).
        """
        response = requests.get(self.endpoint, params=self.params, headers=self.headers)
        response.raise_for_status()  # Raise an error for bad responses
        result_data = response.json()  # Assuming API returns JSON

        wagon = Wagon(name=self.tool_name, data=result_data)
        return wagon
