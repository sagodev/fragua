"""
Cart tools used by Transporters to deliver data.

Carts handle the transfer to various destinations such as databases, files, or APIs.
"""

from core.tool import Tool


class Cart(Tool):
    """
    Base class for Cart tools.
    """

    def use(self, data):
        """
        Deliver data to the final destination.

        Args:
            data: Data retrieved from Boxes.
        """
        # Placeholder: implement loading logic in subclasses
        print(f"Using {self.tool_name} to deliver data...")
