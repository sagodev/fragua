"""
Subclasses of Cart representing specific delivery methods with a unified delivery method.
"""

from sqlalchemy import create_engine
import requests
from .cart import Cart


class ExcelCart(Cart):
    """Cart for delivering data to Excel files."""

    def deliver(self, data, path):
        """
        Deliver data to an Excel file.
        This wraps connect, write, and close into one call.
        """
        try:
            # Connect
            self.file_path = path
            print(f"ExcelCart ready to write to {self.file_path}")

            # Write
            data.to_excel(self.file_path, index=False)
            print(f"ExcelCart wrote data to {self.file_path}")

        finally:
            # Close
            self.file_path = None
            print(f"ExcelCart delivery finished for {path}")


class SQLCart(Cart):
    """Cart for delivering data to SQL databases."""

    def deliver(self, data, connection_string, table_name):
        """
        Deliver data to a SQL database table.
        This wraps connect, write, and close into one call.
        """
        engine = None
        try:
            # Connect
            engine = create_engine(connection_string)
            print("SQLCart connected to database.")

            # Write
            data.to_sql(table_name, engine, if_exists="replace", index=False)
            print(f"SQLCart wrote data to table '{table_name}'.")

        finally:
            # Close
            if engine:
                engine.dispose()
                print("SQLCart delivery finished and connection closed.")


class APICart(Cart):
    """Cart for delivering data to external APIs."""

    def deliver(self, data, api_endpoint, api_key=None):
        """
        Deliver data to an API endpoint.
        This wraps connect, write, and close into one call.
        """
        session = requests.Session()
        try:
            # Connect
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            print(f"APICart ready to send data to {api_endpoint}")

            # Write
            response = session.post(api_endpoint, json=data, headers=headers)
            response.raise_for_status()
            print(f"APICart sent data to API: {api_endpoint}")

        finally:
            # Close
            session.close()
            print(f"APICart delivery finished for {api_endpoint}")
