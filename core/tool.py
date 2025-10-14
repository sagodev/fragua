"""
Base class for all tools used by ETL agents in Fragua.

Examples of tools include Pickaxes, ForgeStyles, and Carts.
"""

from abc import ABC, abstractmethod


class Tool(ABC):
    """
    Abstract base class for tools.
    """

    def __init__(self, tool_name: str):
        """
        Initialize the tool with a given name.

        Args:
            tool_name (str): Name of the tool.
        """
        self.tool_name = tool_name

    @abstractmethod
    def use(self, data):
        """
        Apply the tool to the given data.

        Args:
            data: Input data to be processed or transformed.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} tool_name={self.tool_name}>"
