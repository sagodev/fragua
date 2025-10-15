"""
Subclasses of Cart representing specific delivery methods with a unified delivery method.
"""

from sqlalchemy import create_engine
from .cart import Cart, register_cart
import requests


@register_cart("excel")
class ExcelCart(Cart):
    """Cart for delivering data to Excel files."""

    def deliver(self, data, path, storage=None, container_name=None):
        # Entrega a archivo Excel
        data.to_excel(path, index=False)
        print(f"ExcelCart delivered data to {path}")

        # Actualiza Container si se proporciona StorageManager
        if storage and container_name:
            storage.save_container(container_name, data)
            print(f"ExcelCart stored data in container '{container_name}'")


@register_cart("sql")
class SQLCart(Cart):
    """Cart for delivering data to SQL databases."""

    def deliver(
        self, data, connection_string, table_name, storage=None, container_name=None
    ):
        engine = create_engine(connection_string)
        data.to_sql(table_name, engine, if_exists="replace", index=False)
        engine.dispose()
        print(f"SQLCart delivered data to table '{table_name}'")

        if storage and container_name:
            storage.save_container(container_name, data)
            print(f"SQLCart stored data in container '{container_name}'")


@register_cart("api")
class APICart(Cart):
    """Cart for delivering data to external APIs."""

    def deliver(
        self, data, api_endpoint, api_key=None, storage=None, container_name=None
    ):
        session = requests.Session()
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        response = session.post(api_endpoint, json=data, headers=headers)
        response.raise_for_status()
        session.close()
        print(f"APICart delivered data to API: {api_endpoint}")

        if storage and container_name:
            storage.save_container(container_name, data)
            print(f"APICart stored data in container '{container_name}'")
