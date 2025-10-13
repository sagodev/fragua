"""SQL pickaxe - executes a query and returns results as a Bagon.

Requires SQLAlchemy (and optionally a DB driver).
"""

from typing import Optional
import pandas as pd
from ...miners.pickaxes.base_pickaxe import Pickaxe
from ...storage.bagons import Bagon

class SQLPickaxe(Pickaxe):
    """
    SQLPickaxe executes a SQL query against a database connection string.

    Args:
        connection_string: SQLAlchemy connection string (e.g. 'sqlite:///db.sqlite').
        query: SQL query to run.
        name: optional logical name.
    """
    def __init__(self, connection_string: str, query: str, name: Optional[str] = None, read_kwargs: Optional[dict] = None):
        super().__init__(name=name or f"sql:{query[:20]}")
        self.connection_string = connection_string
        self.query = query
        self.read_kwargs = read_kwargs or {}

    def extract(self) -> Bagon:
        try:
            # Lazy import to avoid strict dependency if user doesn't need SQL
            from sqlalchemy import create_engine
        except Exception as e:
            raise RuntimeError("SQLPickaxe requires sqlalchemy. Install with `pip install sqlalchemy`.") from e

        engine = create_engine(self.connection_string)
        with engine.connect() as conn:
            df = pd.read_sql(self.query, con=conn, **self.read_kwargs)
        bagon = Bagon(name=self.name, data=df)
        bagon.metadata.update({"source": "sql", "connection": self.connection_string})
        return bagon
