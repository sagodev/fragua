"""
Pickaxe tools used by Miners to extract data.

Different Pickaxe types can extract from CSV, Excel, SQL, or other sources.
"""

from typing import Any, Generator, Dict, Type
from core.tool import Tool


# Registry for dynamic pickaxe discovery
PICKAXE_REGISTRY: Dict[str, Type["Pickaxe"]] = {}


def register_pickaxe(name: str):
    """Decorator used to register Pickaxe subclasses dynamically."""

    def wrapper(cls):
        PICKAXE_REGISTRY[name] = cls
        return cls

    return wrapper


class Pickaxe(Tool):
    """
    Optimized base class for Pickaxe tools.

    Implements a flexible and memory-efficient data extraction workflow.
    Subclasses must implement the `extract` method.
    """

    def use(self, source: Any) -> Any:
        """
        Defines the general workflow for data extraction.
        It can handle generators (streaming) or full data structures.
        """
        try:
            data = self.extract(source)
            validated = self.validate(data)
            return self.postprocess(validated)
        except Exception as e:
            self.log_error(e)
            raise

    def extract(self, source: Any) -> Generator | Any:
        """Must be implemented by subclasses to extract data from a source."""
        raise NotImplementedError("Subclasses must implement extract()")

    def validate(self, data: Any) -> Any:
        """Performs a basic validation of the extracted data."""
        if data is None:
            raise ValueError("No data extracted")
        return data

    def postprocess(self, data: Any) -> Any:
        """Optional step for cleaning or formatting data."""
        return data

    def log_error(self, error: Exception) -> None:
        """Basic error logging (can be overridden or integrated with logging libs)."""
        print(f"[Pickaxe ERROR] {type(error).__name__}: {error}")
