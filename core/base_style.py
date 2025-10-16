"""
Base class for all styles used by ETL agents in Fragua.

Examples of styles include Forge Styles, Extraction Styles, and Delivery Styles.
"""

from abc import ABC, abstractmethod


class Style(ABC):
    """
    Abstract base class for style.
    """

    def __init__(self, style_name: str):
        """
        Initialize the style with a given name.

        Args:
            style_name (str): Name of the style.
        """
        self.style_name = style_name

    @abstractmethod
    def use(self, data):
        """
        Apply the style to the given data.

        Args:
            data: Input data to be processed or transformed.
        """
        pass

    def __repr__(self):
        return f"<{self.__class__.__name__} style_name={self.style_name}>"
