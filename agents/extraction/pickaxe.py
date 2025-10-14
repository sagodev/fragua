"""
Pickaxe tools used by Miners to extract data.

Different Pickaxe types can extract from CSV, Excel, SQL, or other sources.
"""

from core.tool import Tool


class Pickaxe(Tool):
    """
    Base class for Pickaxe tools.
    """

    def use(self, data=None):
        """
        Extract data using this Pickaxe.
        To be implemented in subclasses.
        """
        print(f"Using {self.tool_name} to extract data...")
        return None

    def extract(self, **kwargs):
        """
        Unified extraction method.
        Wraps use() and allows future extension (logging, validation, etc.)

        Returns:
            Wagon: Extracted data.
        """
        wagon = self.use(**kwargs)
        print(f"{self.tool_name} extracted data into Wagon: {wagon.name}")
        return wagon
