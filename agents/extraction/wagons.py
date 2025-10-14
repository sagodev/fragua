"""
Bagons for storing extracted data from Miners.

Bagons provide temporary storage and versioning for raw data.
"""


class Wagon:
    """
    Represents a storage container for extracted data.
    """

    def __init__(self, name: str, data=None):
        """
        Initialize a wagon with a name and optional data.

        Args:
            name (str): Name of the wagon.
            data: Optional initial data.
        """
        self.name = name
        self.data = data

    def store(self, data):
        """
        Store data in the wagon.

        Args:
            data: Data to store.
        """
        self.data = data

    def retrieve(self):
        """
        Retrieve data from the wagon.

        Returns:
            Stored data.
        """
        return self.data

    def __repr__(self):
        return f"<Wagon name={self.name} data={'set' if self.data else 'empty'}>"
