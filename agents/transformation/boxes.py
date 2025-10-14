"""
Boxes for storing transformed data from Blacksmiths.

Boxes provide versioned storage for transformed data before loading.
"""


class Box:
    """
    Represents a storage container for transformed data.
    """

    def __init__(self, name: str, data=None):
        """
        Initialize a Box with a name and optional data.

        Args:
            name (str): Name of the Box.
            data: Optional initial data.
        """
        self.name = name
        self.data = data

    def store(self, data):
        """
        Store data in the Box.

        Args:
            data: Data to store.
        """
        self.data = data

    def retrieve(self):
        """
        Retrieve data from the Box.

        Returns:
            Stored data.
        """
        return self.data

    def __repr__(self):
        return f"<Box name={self.name} data={'set' if self.data else 'empty'}>"
